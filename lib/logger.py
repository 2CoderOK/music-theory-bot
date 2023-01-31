"""This is a custom Logger for Telegram Bot application
"""
import logging
import logging.handlers

LOGGER_NAME = "TGBotLogger"

log = None


def get_logger():
    """A function to get a global Logger instance"""
    return logging.getLogger(LOGGER_NAME)


class Logger:
    """This is a custom Logger class"""

    def __init__(
        self,
        filename: str = "tgbot_main.log",
        file: bool = True,
        console: bool = True,
        log_level: int = logging.WARNING,
        max_log_size: int = 50000000,
        log_backup_count: int = 10,
        date_format: str = "",
        logger_name: str = LOGGER_NAME,
    ):
        """A custom Logger constructor.

        Keyword arguments:
        filename -- a path and filename to a log file
        file -- enable output to file
        console -- enable output to console
        log_level -- log level
        max_log_size -- maxium size of a log file
        log_backup_count -- a log backup count
        """ ""
        global log
        log = logging.getLogger(logger_name)
        log.setLevel(log_level)
        if len(date_format) > 0:
            import datetime

            formatted_date = datetime.datetime.strftime(
                datetime.datetime.now(), date_format
            )
            filename = filename.replace("%DATETIME%", formatted_date)
        handler1 = logging.FileHandler(filename, "w", "utf-8")
        handler1 = logging.handlers.RotatingFileHandler(
            filename, maxBytes=max_log_size, backupCount=log_backup_count
        )
        formatter = logging.Formatter(
            "%(levelname)s %(asctime)s [%(funcName)s] %(message)s"
        )
        handler1.setFormatter(formatter)
        handler1.setLevel(log_level)
        handler2 = logging.StreamHandler()
        handler2.setFormatter(formatter)
        handler2.setLevel(log_level)
        if console:
            log.addHandler(handler2)
        if file:
            log.addHandler(handler1)


def trace(fn):
    """A built-in function`s logging

    Keyword arguments:
    fn -- a function to be traced
    """
    # comment next line to enable tracing
    # return fn

    from itertools import chain

    def trace(*v, **k):
        global log

        name = fn.__name__
        log.debug("%s(%s)" % (name, ", ".join(map(repr, chain(v, k.values())))))
        return fn(*v, **k)

    return trace
