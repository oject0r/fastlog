# FastLog

**FastLog** is a high-performance and flexible logging library for Python, designed to handle both synchronous and asynchronous workflows. It supports advanced features like multiple handlers, log rotation, custom formats, and much more.

## 📋 Features

- **Asynchronous and Synchronous Logging**: Choose the mode that fits your application.
- **Multiple Handlers**:
  - Console (`ConsoleHandler`)
  - Files with size or time-based rotation (`RotatingFileHandler`, `TimedRotatingFileHandler`)
  - Custom handlers (e.g., HTTP-based logging).
- **Log Formats**:
  - Plain text (`PlainFormat`)
  - JSON (`JSONFormat`)
- **Callbacks**: Trigger custom logic after processing each log entry.
- **Dynamic Configuration**: Easily configure logging levels, formats, and handlers at runtime.
- **Context Support**: Include rich contextual data in your log messages.

## 🚀 Installation

Clone the FastLog repository:

```bash
git clone https://github.com/oject0r/fastlog.git
cd fastlog
```

*(You can also copy `fastlog.py` into your project, as it does not require any additional dependencies.)*

## 🛠 Usage

### 1. Basic Example (Synchronous)

```python
from fastlog import Logger, LoggerConfig, HandlerConfig, HandlerType, LogLevel

# Configure the logger
logger_config = LoggerConfig(
    handlers=[
        HandlerConfig(handler_type=HandlerType.CONSOLE, level=LogLevel.DEBUG)
    ],
    async_mode=False,  # Synchronous mode
)

# Initialize the logger
logger = Logger(logger_config)

# Log messages
logger.debug("Debugging the application state")
logger.info("Application started")
logger.error("An error occurred")
```

---

### 2. Advanced Example (Asynchronous with Callbacks)

```python
import asyncio
from fastlog import Logger, LoggerConfig, HandlerConfig, HandlerType, LogLevel, LogFormat
from pathlib import Path

async def main():
    def log_callback(log_entry):
        print(f"Callback triggered: {log_entry}")

    logger_config = LoggerConfig(
        handlers=[
            HandlerConfig(
                handler_type=HandlerType.CONSOLE,
                level=LogLevel.DEBUG,
                format=LogFormat.PLAIN,
            ),
            HandlerConfig(
                handler_type=HandlerType.FILE,
                level=LogLevel.INFO,
                format=LogFormat.JSON,
                filename=Path("logs/app.log"),
                rotate_size=10 * 1024 * 1024,  # 10 MB
                rotate_count=3,
            ),
        ],
        callback=log_callback,
        async_mode=True,
    )

    logger = Logger(logger_config)
    await logger.start()

    # Log various levels with context
    logger.debug("Debugging application state", user="DevUser", module="testing")
    logger.info("Application started successfully", user="Admin")
    logger.warning("Potential issue detected", retry_count=2, module="network")
    logger.error("Error processing request", user="Client", error_code=404)
    logger.critical("System failure imminent!", system="Database", recovery_needed=True)

    await asyncio.sleep(1)
    await logger.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📂 Examples

Check out more usage examples in the [examples directory](examples/):
- `console_keyword_filter.py`: Logging with filtering by keywords.
- `time_based_file_rotation.py`: File logging with time-based rotation.
- `http_log_handler.py`: Sending logs to an external HTTP service.
- `custom_formatter.py`: Using custom log formatters.

---

## 🤝 Contributing

We welcome contributions! Feel free to open an issue or submit a pull request.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🛡 Support

If you encounter any issues or have questions, feel free to open an issue on GitHub.
