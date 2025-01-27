import logging

format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

logging.basicConfig(format=format, level=logging.INFO)


def Logger(module) -> logging.Logger:
    return logging.getLogger(module)
