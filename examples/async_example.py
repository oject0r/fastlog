import asyncio
from pathlib import Path
from fastlog import Logger, LoggerConfig, HandlerConfig, HandlerType, LogLevel, LogFormat

async def main():
    # Callback to handle log entries
    def log_callback(log_entry):
        print(f"Log callback triggered: {log_entry}")

    # Logger configuration
    logger_config = LoggerConfig(
        handlers=[
            HandlerConfig(  # Console handler for debug logs
                handler_type=HandlerType.CONSOLE,
                level=LogLevel.DEBUG,
                format=LogFormat.PLAIN
            ),
            HandlerConfig(  # File handler for info logs and above
                handler_type=HandlerType.FILE,
                level=LogLevel.INFO,
                format=LogFormat.JSON,
                filename=Path("../logs/app.log"),
                rotate_size=10 * 1024 * 1024,  # 10 MB
                rotate_count=3,
            ),
        ],
        callback=log_callback,  # Optional callback for each log entry
        async_mode=True,  # Enable asynchronous logging
    )

    # Initialize and start the logger
    logger = Logger(logger_config)
    await logger.start()

    # Log messages with various levels and context
    logger.debug("Debugging application state", user="developer", module="testing")
    logger.info("Application started successfully", user="admin")
    logger.warning("Potential issue detected", retry_count=2, module="network")
    logger.error("Error processing request", user="client", error_code=404)
    logger.critical("System failure imminent!", system="database", recovery_needed=True)

    # Allow time for asynchronous logs to process
    await asyncio.sleep(1)

    # Shutdown logger gracefully
    await logger.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
