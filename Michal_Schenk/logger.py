import logging
import os

if not os.path.exists("logs"):
    os.makedirs("logs")

def get_logger(name:str):
    """Returns the logger

    Args:
        name (str): used to organize multiple loggers

    Returns:
        Logger: the logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)

        # File handler
        file = logging.FileHandler(f"logs/{name}.log")
        file.setLevel(logging.DEBUG)

        fmt = logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
        )
        console.setFormatter(fmt)
        file.setFormatter(fmt)

        logger.addHandler(console)
        logger.addHandler(file)

    return logger