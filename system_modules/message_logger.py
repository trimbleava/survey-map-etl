# standard libs
import logging
import os, sys


# todo good code also on this command:
# path = os.environ["PROJ_DATA"]
# logger.dbug("PROJ data found in package: path=%r.", path)
# see D:\PROJECTS\PY-ENV\Lib\site-packages\fiona\env.py

# app modules

logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(message)s', level="INFO")
logger = logging.getLogger(__name__)


class MessageLogger():
    
    def __init__(self, logger_name="default.log", logger_dir=None):
        # initialized in house_keeping
        self.logger_name = os.getenv("LOGGER_NAME", logger_name)
        self.log_dir = os.getenv("LOG_DIR", logger_dir)

        if self.log_dir is None:
            self.log_dir = os.getcwd()
        
        self.log_file = os.path.join(self.log_dir, self.logger_name)
        self._configure()
        

    def _configure(self):
        # create a top-level logger, prevent from propagating messages to the root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.propagate = False

        # create a console handler with a higher log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColorFormatter())

        # create a file handler
        # file_handler = logging.handlers.TimedRotatingFileHandler(log_file, 'M', 1, 5)
        file_handler = logging.FileHandler(self.log_file)
        
        file_handler.setLevel(logging.INFO)
        frmt = logging.Formatter("%(filename)s:%(lineno)d> | %(message)s | %(levelname)s | %(asctime)s")
        file_handler.setFormatter(frmt)

        # add handlers to log
        # not to duplicate per call to logger
        if (logger.hasHandlers()):
            logger.handlers.clear()
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        self._logger = logger
       

    @property
    def logger(self):
        return self._logger


class ColorFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""
 
    grey   = "\x1b[90m"
    green  = "\x1b[92m"
    yellow = "\x1b[93m"
    red    = "\x1b[91m"
    reset  = "\x1b[0m"

    format = "%(filename)s:%(lineno)d> | %(message)s"
   
    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: red + format + reset
    }
 
    def format(self, record):
        record.levelname = 'WARN' if record.levelname == 'WARNING' else record.levelname
        record.levelname = 'ERROR' if record.levelname == 'CRITICAL' else record.levelname
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def start():
    # instatiate logger
    global ml
    ml = MessageLogger()
    logger = ml.logger
    msg = "Starting MessageLogger\n"
    logger.info(msg)
  
    return logger


def configure_logging(logger_name="default.log"):    # to delete

    # initialized in house_keeping
    log_name = os.getenv("LOGGER_NAME", logger_name)
    log_dir = os.getenv("LOG_DIR", None)
    if log_dir is None:
        log_dir = os.getcwd()
        
    log_file = os.path.join(log_dir, log_name)
      
    # create a top-level logger, prevent from propagating messages to the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # create a console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColorFormatter())

    # create a file handler
    # file_handler = logging.handlers.TimedRotatingFileHandler(log_file, 'M', 1, 5)
    file_handler = logging.FileHandler(log_file)
    
    file_handler.setLevel(logging.INFO)
    frmt = logging.Formatter("%(filename)s:%(lineno)d> | %(message)s | %(levelname)s | %(asctime)s")
    file_handler.setFormatter(frmt)

    # add handlers to log
    # not to duplicate per call to logger
    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
