import logging
import os
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init(autoreset=True)


class ColorFormatter(logging.Formatter):
    """
    Custom logging formatter to color-code log messages based on their source.

    """

    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        self.host_color = Fore.BLUE
        self.guesser_color = Fore.GREEN
        self.other_color = Fore.YELLOW
        self.reset = Style.RESET_ALL

    def format(self, record):
        message = record.getMessage()
        if message.startswith("Host"):
            record.msg = f"{self.host_color}{message}{self.reset}"
        elif message.startswith("Guesser"):
            record.msg = f"{self.guesser_color}{message}{self.reset}"
        else:
            record.msg = f"{self.other_color}{message}{self.reset}"
        return super().format(record)


def setup_logger(game_id: str) -> logging.Logger:
    """
    Set up and configure the logger for the game.

    :param game_id: Unique identifier for the game instance
    :return: Configured logger instance
    """
    # Ensure the log directory exists
    log_dir = "game_logs"
    os.makedirs(log_dir, exist_ok=True)

    # Configure logging to both console and file with color formatting
    log_filename = f"{log_dir}/game_log_{game_id}.log"
    logger = logging.getLogger(f"game_{game_id}")
    logger.setLevel(logging.INFO)

    # Prevent log messages from being propagated to the root logger
    logger.propagate = False

    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handler with color formatter
    console_handler = logging.StreamHandler()
    console_formatter = ColorFormatter()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler without color codes
    file_handler = logging.FileHandler(log_filename)
    file_formatter = logging.Formatter("%(asctime)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger
