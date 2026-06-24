"""Structured logging configuration."""

import logging
import sys


def configure_logging() -> None:
    """Configure consistent service logging."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

