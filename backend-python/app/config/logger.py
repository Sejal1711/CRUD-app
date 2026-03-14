import sys
from loguru import logger
from app.config.settings import settings

# Remove default handler
logger.remove()

# Console — colored
logger.add(
    sys.stdout,
    level="DEBUG" if settings.ENV == "development" else "INFO",
    format="<green>{time:HH:mm:ss}</green> [<level>{level}</level>]: {message}",
    colorize=True,
)

# Rotating file — info+
logger.add(
    "logs/app-{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="14 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} [{level}]: {message}",
)

# Error-only log
logger.add(
    "logs/error-{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} [{level}]: {message}\n{exception}",
)
