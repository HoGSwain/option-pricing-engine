"""
Structured logging setup.

Reuses the exact Loguru configuration from Projects 1-5 so log output is
consistent across the AIFEL portfolio.
"""

import sys

from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | "
    "<cyan>{module}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)

__all__ = ["logger"]
