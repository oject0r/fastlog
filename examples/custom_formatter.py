from fastlog import Logger, LoggerConfig, HandlerConfig, HandlerType, LogLevel
import logging


class CustomFormatter(logging.Formatter):
	"""Custom formatter for log messages."""
	def __init__(self, fmt=None, datefmt=None):
		super().__init__(fmt, datefmt)

	def format(self, record):
		# Add the asctime field to the record
		record.asctime = self.formatTime(record, self.datefmt)
		return f"[{record.levelname}] {record.asctime}: {record.getMessage()}"


def main():
	# Configure logger with a custom formatter
	handler = HandlerConfig(handler_type=HandlerType.CONSOLE, level=LogLevel.DEBUG)
	logger_config = LoggerConfig(
		handlers=[handler],
		async_mode=False,
	)
	logger = Logger(logger_config)

	# Set custom formatter
	for handler in logger.logger.handlers:
		handler.setFormatter(CustomFormatter())

	# Log messages
	logger.debug("Custom debug message.")
	logger.info("Custom info message.")
	logger.error("Custom error message.")


if __name__ == "__main__":
	main()
