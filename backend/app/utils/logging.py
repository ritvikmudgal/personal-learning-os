"""Structured logging configuration for the application."""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", name: Optional[str] = None) -> logging.Logger:
    """Configure and return a logger with structured formatting.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        name: Logger name. If None, configures the root logger.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name or "learning_os")

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Console handler with structured format
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logger.level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a child logger under the application logger hierarchy.

    Args:
        name: Module or component name for the logger.

    Returns:
        Logger instance.
    """
    return logging.getLogger(f"learning_os.{name}")
