"""CLI diagnostics always go to stderr."""
import logging
import sys


def configure_logging():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(levelname)s: %(message)s")
