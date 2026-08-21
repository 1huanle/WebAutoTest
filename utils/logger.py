import sys

from loguru import logger

from config.config import Config

logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    level=Config.LOG_LEVEL,
    colorize=True,
)
logger.add(
    Config.LOG_DIR / "test_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="100 MB",
    retention="30 days",
    encoding="utf-8",
)
logger.add(
    Config.LOG_DIR / "error_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="100 MB",
    retention="30 days",
    encoding="utf-8",
)
