import logging
import requests  # you can install it, not used in requirements
from fastlog import Logger, LoggerConfig, HandlerConfig, HandlerType, LogLevel

class HTTPHandler(logging.Handler):
    """Custom handler to send logs to an external HTTP service."""
    def __init__(self, endpoint):
        super().__init__()
        self.endpoint = endpoint

    def emit(self, record):
        log_entry = self.format(record)
        try:
            requests.post(self.endpoint, json={"log": log_entry})
        except requests.RequestException as e:
            print(f"Failed to send log: {e}")

def main():
    # Configure logger with HTTP handler
    http_handler = HTTPHandler(endpoint="https://example.com/logs")
    http_handler.setLevel(logging.INFO)

    logger_config = LoggerConfig(async_mode=False)
    logger = Logger(logger_config)
    logger.logger.addHandler(http_handler)

    # Log messages
    logger.info("Log sent to external service.")
    logger.error("Critical error reported.")

if __name__ == "__main__":
    main()
