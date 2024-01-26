import discord
import logging
from logging.handlers import TimedRotatingFileHandler
import os


def setup_logger(*, log_directory: str = "./logs/"):
    os.makedirs(log_directory, exist_ok=True)

    discord.utils.setup_logging()

    logger = logging.getLogger("root")
    logger.setLevel(logging.DEBUG)

    file_handler = TimedRotatingFileHandler(
        filename="./logs/bot.log",
        when="midnight",
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setFormatter(
        logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', "%Y-%m-%d %H:%M:%S", style='{')
    )

    logger.addHandler(file_handler)

    return logger
