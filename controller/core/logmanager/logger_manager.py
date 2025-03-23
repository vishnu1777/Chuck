import logging
import os

class LoggerManager:
    """Manages logging configuration for the application."""

    def __init__(self, class_name):
        self.LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")  
        self.LOG_FILE_PATH = os.path.join(self.LOG_DIR, "test_logs.log")  

        os.makedirs(self.LOG_DIR, exist_ok=True)

        if os.path.isdir(self.LOG_FILE_PATH):  
            os.rmdir(self.LOG_FILE_PATH)  
        elif os.path.exists(self.LOG_FILE_PATH):
            os.chmod(self.LOG_FILE_PATH, 0o666)  

        # ✅ Create a logger
        self.logger = logging.getLogger(class_name)
        self.logger.setLevel(logging.DEBUG)  # ✅ Allows DEBUG, INFO, ERROR

        # ✅ Prevent logger from propagating to root logger
        self.logger.propagate = False  

        # ✅ Set up file handler for logging
        try:
            file_handler = logging.FileHandler(self.LOG_FILE_PATH, mode="a",encoding="utf-8")  
            file_handler.setLevel(logging.DEBUG)  # ✅ Capture all levels

            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)

            if not self.logger.hasHandlers():  # ✅ Prevent duplicate handlers
                self.logger.addHandler(file_handler)
        except PermissionError:
            print(f"⚠️ PermissionError: Cannot write to {self.LOG_FILE_PATH}. Run script as Administrator.")

    def log_info(self, *messages):
        self.logger.info(" ".join(map(str, messages)))

    def log_debug(self, *messages):
        self.logger.debug(" ".join(map(str, messages)))  # ✅ Now properly logs DEBUG

    def log_error(self, *messages):
        self.logger.error(" ".join(map(str, messages)))

    def log(self, log_type, *messages):
        """Logs dynamically based on log_type."""
        log_methods = {
            "info": self.log_info,
            "debug": self.log_debug,
            "error": self.log_error
        }
        log_method = log_methods.get(log_type.lower())
        if log_method:
            log_method(*messages)
        else:
            self.logger.warning(f"⚠️ Invalid log type '{log_type}'. Messages: {' '.join(map(str, messages))}")  
