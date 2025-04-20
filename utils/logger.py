import copy
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

LOG_DIR = "data/logs"

class CustomFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[0;36m",  # CYAN
        "INFO": "\033[0;32m",  # GREEN
        "WARNING": "\033[0;33m",  # YELLOW
        "ERROR": "\033[0;31m",  # RED
        "CRITICAL": "\033[0;37;41m",  # WHITE ON RED
        "RESET": "\033[0m",  # RESET COLOR
    }

    def format(self, record):
        colored_record = copy.copy(record)
        levelness = colored_record.levelname
        color = self.COLORS.get(levelness, self.COLORS["RESET"])
        colored_record.levelness = f"{color}{levelness}{self.COLORS['RESET']}"
        return super().format(colored_record)

class CustomLogger(logging.Logger):
    def __init__(self, name: str):
        super().__init__(name, level=logging.DEBUG)
        self._configure_handlers()
    
    def _configure_handlers(self):
        if self.handlers:
            return

        date_str = datetime.now().strftime('%d-%m-%Y')
        dated_log_dir = os.path.join(LOG_DIR, date_str)
        os.makedirs(dated_log_dir, exist_ok=True)
        
        formatter = CustomFormatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        log_file = os.path.join(dated_log_dir, f"{self.name}.log")

        rotating_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
        rotating_handler.setFormatter(formatter)
        self.addHandler(rotating_handler)