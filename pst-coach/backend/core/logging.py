"""
Logging configuration using loguru.
"""
import sys
from loguru import logger
from core.config import settings


def setup_logging():
    """Configure application logging."""
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        format=log_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        format=log_format,
        level=settings.LOG_LEVEL,
        enqueue=True
    )

    if settings.SENTRY_DSN:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            traces_sample_rate=1.0 if settings.ENVIRONMENT == "production" else 0.1
        )

    return logger
