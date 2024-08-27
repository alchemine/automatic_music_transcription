"""Logging module."""

import json
import logging

from config.load import ENV


# https://pkg.go.dev/github.com/shafiqaimanx/pastax/colors
STYLES = {
    "ENDC": "\033[0m",
    "BOLD": "\033[1m",
    "ITALIC": "\033[3m",
    "UNDERLINE": "\033[4m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "DARKGRAY": "\033[90m",
    "LIGHTRED": "\033[91m",
    "PINK": "\033[95m",
    "FIREBRICK": "\033[38;5;124m",
    "ORANGERED": "\033[38;5;202m",
    "TOMATO": "\033[38;5;203m",
    "GRAPEFRUIT": "\033[38;5;208m",
    "DARKORANGE": "\033[38;5;214m",
    "OKRED": "\033[91m",
    "OKGREEN": "\033[92m",
    "OKYELLOW": "\033[93m",
    "OKBLUE": "\033[94m",
    "OKMAGENTA": "\033[95m",
    "OKCYAN": "\033[96m",
}


def setup_logger() -> logging.Logger:
    """Setup logger.

    Returns:
        logging.Logger: The logger object.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        # "[%(asctime)s] %(levelname)s [%(pathname)s.%(funcName)s():l%(lineno)d] %(message)s",
        "[%(asctime)s] %(levelname)-7s | %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )

    # Log to console using StreamHandler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def pretty_dict(s: str) -> str:
    """Pretty print dictionary.

    Args:
        s (str): The dictionary to pretty print.

    Returns:
        str: The pretty printed dictionary.
    """
    json_str = json.dumps(s, indent=2, ensure_ascii=False)
    json_str = json_str.replace('\\"', "'")
    return json_str


def slog(
    msg: str, style: str | None = None, level: str = "info", dump: bool = True
) -> str:
    """Stylish log message.

    Args:
        msg (str): The message to log.
        style (str): The style of the message.
        level (str): The log level.
        dump (bool): The dump flag.

    Returns:
        str: The stylish message.
    """
    try:
        if dump:
            msg = pretty_dict(msg)
            msg = msg.strip('"')  # remove redundant quotes
    except:
        pass

    if ENV != "local":
        stylish_msg = msg
    elif style:
        stylish_msg = f"{STYLES[style]}{msg}{STYLES['ENDC']}"
    else:
        stylish_msg = msg

    match level:
        case "info":
            logger.info(stylish_msg)
        case "error":
            logger.error(stylish_msg)
        case "warning":
            logger.warning(stylish_msg)
        case "debug":
            logger.debug(stylish_msg)
        case _:
            print(stylish_msg)

    return stylish_msg


def log_info(msg: str, dump: bool = True) -> None:
    """Stylish info log.

    Args:
        msg (str): The message to log.
        dump (bool): The dump flag. Defaults to True.
    """
    slog(msg, style="OKBLUE", dump=dump)  # OKCYAN


def log_success(msg: str, dump: bool = True) -> None:
    """Stylish success log.

    Args:
        msg (str): The message to log.
        dump (bool): The dump flag. Defaults to True.
    """
    slog(msg, style="GREEN", dump=dump)


def log_error(msg: str, dump: bool = False) -> None:
    """Stylish error log.

    Args:
        msg (str): The message to log.
        dump (bool): The dump flag. Defaults to True.
    """
    slog(msg, style="TOMATO", level="error", dump=dump)


def log_warning(msg: str, dump: bool = False) -> None:
    """Stylish warning log.

    Args:
        msg (str): The message to log.
        dump (bool): The dump flag. Defaults to True.
    """
    slog(msg, style="GRAPEFRUIT", level="warning", dump=dump)


def log_api(msg: str, error: bool = False) -> None:
    """Stylish api log.

    Args:
        msg (str): The message to log.
        error (bool): The error status of the API. Defaults to False.
    """
    if error:
        log_error("Request API:")
        log_error(msg, dump=True)
    else:
        log_success("Request API:")
        log_success(msg)


logger = setup_logger()


if __name__ == "__main__":
    log_info("This is an info message.")
    log_success("This is a success message.")
    log_error("This is an error message.")
    log_warning("This is a warning message.")
    log_api("This is an API message.")
    for style in STYLES:
        slog(f"This is a {style} message.", style=style)
