import asyncio
import logging
import json
from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Callable, Union, List, Dict
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Enums for Log Configuration
class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @staticmethod
    def from_str(level_str: str) -> 'LogLevel':
        level_str = level_str.upper()
        if level_str in LogLevel.__members__:
            return LogLevel[level_str]
        raise ValueError(f"Unknown log level: {level_str}")

class LogFormat(Enum):
    PLAIN = "PLAIN"
    JSON = "JSON"

class HandlerType(Enum):
    CONSOLE = "CONSOLE"
    FILE = "FILE"

# Configuration Classes
class HandlerConfig:
    def __init__(
        self,
        handler_type: HandlerType = HandlerType.CONSOLE,
        level: LogLevel = LogLevel.INFO,
        format: LogFormat = LogFormat.PLAIN,
        filename: Optional[Path] = None,
        rotate_size: Optional[int] = None,
        rotate_count: int = 5,
        rotate_when: Optional[str] = None,
        timestamp_format: str = "%Y-%m-%d %H:%M:%S",
    ):
        self.handler_type = handler_type
        self.level = level
        self.format = format
        self.filename = filename
        self.rotate_size = rotate_size
        self.rotate_count = rotate_count
        self.rotate_when = rotate_when
        self.timestamp_format = timestamp_format

class LoggerConfig:
    def __init__(
        self,
        handlers: Optional[List[HandlerConfig]] = None,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        async_mode: bool = False,
    ):
        self.handlers = handlers or [HandlerConfig()]
        self.callback = callback
        self.async_mode = async_mode

# Logger Implementation
class Logger:
    LEVEL_MAP = {
        LogLevel.DEBUG: logging.DEBUG,
        LogLevel.INFO: logging.INFO,
        LogLevel.WARNING: logging.WARNING,
        LogLevel.ERROR: logging.ERROR,
        LogLevel.CRITICAL: logging.CRITICAL,
    }

    def __init__(self, config: LoggerConfig):
        self.config = config
        self.logger = logging.getLogger("AdvancedLogger")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        for handler_cfg in self.config.handlers:
            handler = self._create_handler(handler_cfg)
            self.logger.addHandler(handler)

        self.log_queue = asyncio.Queue() if config.async_mode else None
        self._stop_event = None
        self._queue_task = None

    def _create_handler(self, cfg: HandlerConfig) -> logging.Handler:
        if cfg.handler_type == HandlerType.CONSOLE:
            handler = logging.StreamHandler()
        elif cfg.handler_type == HandlerType.FILE:
            if not cfg.filename:
                raise ValueError("File handler requires a filename.")
            # Ensure the directory exists
            cfg.filename.parent.mkdir(parents=True, exist_ok=True)

            if cfg.rotate_size:
                handler = RotatingFileHandler(
                    filename=cfg.filename,
                    maxBytes=cfg.rotate_size,
                    backupCount=cfg.rotate_count,
                    encoding="utf-8",
                )
            elif cfg.rotate_when:
                handler = TimedRotatingFileHandler(
                    filename=cfg.filename,
                    when=cfg.rotate_when,
                    backupCount=cfg.rotate_count,
                    encoding="utf-8",
                )
            else:
                handler = logging.FileHandler(
                    filename=cfg.filename, encoding="utf-8"
                )
        else:
            raise ValueError(f"Unsupported handler type: {cfg.handler_type}")

        handler.setLevel(self.LEVEL_MAP[cfg.level])
        handler.setFormatter(
            JSONFormatter(cfg.timestamp_format)
            if cfg.format == LogFormat.JSON
            else PlainFormatter(cfg.timestamp_format)
        )
        return handler

    async def start(self):
        if self.config.async_mode:
            self._stop_event = asyncio.Event()
            self._queue_task = asyncio.create_task(self._process_log_queue())

    async def shutdown(self):
        if self.config.async_mode and self._stop_event:
            self._stop_event.set()
            if self._queue_task:
                await self._queue_task

    def log(self, level: LogLevel, message: str, **context: Any):
        if self.LEVEL_MAP[level] < self.logger.level:
            return

        log_entry = {
            "level": level.value,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
            "context": context,
        }

        if self.config.async_mode and self.log_queue:
            asyncio.create_task(self.log_queue.put(log_entry))
        else:
            self._process_log_entry(log_entry)

    def _process_log_entry(self, log_entry: Dict[str, Any]):
        self._emit_log(log_entry)
        if self.config.callback:
            try:
                self.config.callback(log_entry)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")

    async def _process_log_queue(self):
        while not self._stop_event.is_set() or not self.log_queue.empty():
            log_entry = await self.log_queue.get()
            self._process_log_entry(log_entry)
            self.log_queue.task_done()

    def _emit_log(self, log_entry: Dict[str, Any]):
        self.logger.log(
            self.LEVEL_MAP[LogLevel[log_entry["level"]]],
            log_entry["message"],
            extra={"context": log_entry.get("context", {})},
        )

    def debug(self, message: str, **context: Any):
        self.log(LogLevel.DEBUG, message, **context)

    def info(self, message: str, **context: Any):
        self.log(LogLevel.INFO, message, **context)

    def warning(self, message: str, **context: Any):
        self.log(LogLevel.WARNING, message, **context)

    def error(self, message: str, **context: Any):
        self.log(LogLevel.ERROR, message, **context)

    def critical(self, message: str, **context: Any):
        self.log(LogLevel.CRITICAL, message, **context)

# Formatters
class PlainFormatter(logging.Formatter):
    def __init__(self, timestamp_format: str):
        super().__init__(fmt="[{asctime}] [{levelname}] {message} {context}", style="{")
        self.timestamp_format = timestamp_format

    def format(self, record: logging.LogRecord) -> str:
        record.asctime = datetime.fromtimestamp(record.created).strftime(
            self.timestamp_format
        )
        record.context = " ".join(
            f"{k}={v}" for k, v in record.__dict__.get("context", {}).items()
        )
        return super().format(record)

class JSONFormatter(logging.Formatter):
    def __init__(self, timestamp_format: str):
        self.timestamp_format = timestamp_format
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "level": record.levelname,
            "timestamp": datetime.fromtimestamp(record.created).strftime(
                self.timestamp_format
            ),
            "message": record.getMessage(),
            "context": record.__dict__.get("context", {}),
        }
        return json.dumps(log_entry)