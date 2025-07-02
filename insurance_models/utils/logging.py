import logging
import sys

def setup_logging(level=logging.INFO):
    """Sets up basic logging configuration."""
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout
    )
