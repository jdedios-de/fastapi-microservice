import logging
import sys
from typing import Optional
from pythonjsonlogger.json import JsonFormatter

from app.config import settings  # Assuming settings has LOG_LEVEL and other config


def get_logger(name: Optional[str] = None) -> logging.Logger:
    # Use provided name or default to module name
    logger = logging.getLogger(name or __name__)

    # Avoid duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    # Set log level from settings or default to INFO
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create console handler with a JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Define JSON log format
    formatter = JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s %(filename)s %(lineno)d"
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False

    return logger