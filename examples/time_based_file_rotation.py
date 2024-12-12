from fastlog import Logger, LoggerConfig, HandlerConfig, HandlerType, LogLevel, LogFormat
from pathlib import Path

def main():
    # Configure time-based log rotation
    handler = HandlerConfig(
        handler_type=HandlerType.FILE,
        level=LogLevel.INFO,
        format=LogFormat.PLAIN,
        filename=Path("logs/daily.log"),
        rotate_when="midnight",  # Rotate log files daily
    )
    logger_config = LoggerConfig(
        handlers=[handler],
        async_mode=False,
    )
    logger = Logger(logger_config)

    # Log some messages
    logger.info("Daily log message 1")
    logger.info("Daily log message 2")

if __name__ == "__main__":
    main()
