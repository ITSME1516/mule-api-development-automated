"""
Logging Configuration Module
Provides centralized logging setup for the MuleSoft API Creator application.
Ensures consistent logging across all modules for better tracking and debugging.
"""

import logging
import sys
from datetime import datetime


def setup_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up and configure a logger with consistent formatting.
    
    Args:
        name (str): The name of the logger (typically __name__)
        log_level (int): The logging level (default: logging.INFO)
    
    Returns:
        logging.Logger: Configured logger instance
    
    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Application started")
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Prevent duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Create console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter with timestamp, level, and message
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


class LoggerMixin:
    """
    Mixin class to provide logging capability to any class.
    Automatically creates a logger based on the class name.
    
    Usage:
        class MyClass(LoggerMixin):
            def __init__(self):
                super().__init__()
                # Logger is now available as self.logger
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize logger for the class."""
        self.logger = setup_logger(self.__class__.__name__)
        super().__init__(*args, **kwargs)
