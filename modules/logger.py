import logging
from logging.handlers import RotatingFileHandler
import sys
import io
import os
from datetime import datetime

class UTF8StreamHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__(stream=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'))

def setup_logger():
    logger = logging.getLogger("VoiceVoxAnki")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"voicevox_anki_{timestamp}.log")

    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = UTF8StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger