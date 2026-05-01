import logging
import sys

import structlog

from src.common.config import Environment, settings


def setup_logger(
    *, level: int = logging.DEBUG if settings.environment in (Environment.local, Environment.dev) else logging.INFO
) -> None:
    """
    Configures the logging system for the application using structlog.

    Parameters
    ----------
    level : int
        The logging level to set for the root logger.
    """
    root = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    processor = (
        structlog.dev.ConsoleRenderer(colors=sys.stdout.isatty())
        if settings.environment == Environment.local
        else structlog.processors.JSONRenderer()
    )
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=processor,
        foreign_pre_chain=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso", utc=True),
        ],
    )

    for h in list(root.handlers):
        root.removeHandler(h)

    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(level)

    for name in [
        "httpx",
        "httpcore",
        "h11",
        "python_multipart",
        "multipart",
        "watchfiles",
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
    ]:
        logging.getLogger(name).setLevel(logging.WARNING)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
