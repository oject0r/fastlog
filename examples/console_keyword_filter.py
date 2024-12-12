from fastlog import Logger, LoggerConfig, HandlerConfig, HandlerType, LogLevel
import logging


class KeywordFilter(logging.Filter):
	"""Filter logs containing specific keywords."""

	def __init__(self, keywords):
		super().__init__()
		self.keywords = keywords

	def filter(self, record):
		return any(keyword in record.getMessage() for keyword in self.keywords)


def main():
	# Configure logger with a filter
	handler = HandlerConfig(handler_type=HandlerType.CONSOLE, level=LogLevel.DEBUG)
	logger_config = LoggerConfig(
		handlers=[handler],
		async_mode=False,
	)
	logger = Logger(logger_config)

	# Add filter to handler
	for handler in logger.logger.handlers:
		handler.addFilter(KeywordFilter(keywords=["important", "alert"]))

	# Log messages
	logger.debug("This is a debug message.")
	logger.info("This is an important message.")
	logger.error("This is an alert for the system.")


if __name__ == "__main__":
	main()
