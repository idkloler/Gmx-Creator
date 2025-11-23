import logging
from colorlog import ColoredFormatter
from .color import C, Fore

red = '\x1b[31m'
green = '\x1b[32m'
yellow = '\x1b[33m'
blue = '\x1b[34m'
pink = '\x1b[35m'
cyan = '\x1b[36m'
reset = '\x1b[0m'
FORMATS = {
    "DBG": "yellow",
    "INF": "cyan",
    "WRN": "yellow",
    "ERR": "red",
    "SUC": "green",
}

class Console(logging.Logger):
    def __init__(self, level = 0):
        super().__init__("main", level)
        class ShortLevelNameFilter(logging.Filter):
            def filter(self, record):
                if record.levelname == "ERROR":
                    record.levelname = "ERR"
                elif record.levelname == "INFO":
                    record.levelname = "INF"
                elif record.levelname == "DEBUG":
                    record.levelname = "DBG"
                elif record.levelname == "WARNING":
                    record.levelname = "WRN"
                elif record.levelno == 25:
                    record.levelname = "SUC"
                return True

        LOGFORMAT = f"{C["gray"]}"+'[%(asctime)s]%(reset)s %(log_color)s[%(levelname)s]%(reset)s | %(message)s'
        formatter = ColoredFormatter(LOGFORMAT, log_colors=FORMATS, datefmt="%H:%M:%S")
        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        stream.setLevel(logging.DEBUG)
        stream.addFilter(ShortLevelNameFilter())
        self.addHandler(stream)
        logging.addLevelName(25, "SUC")
    def info(self, msg, *args, exc_info = None, stack_info = False, stacklevel = 1, extra = None):
        return super().info(f"{C["cyan"]}{msg}{Fore.RESET}", *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra=extra)
    def error(self, msg, *args, exc_info = None, stack_info = False, stacklevel = 1, extra = None):
        return super().error(f"{C["red"]}{msg}{Fore.RESET}", *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra=extra)
    def success(self, msg, *args, exc_info = None, stack_info = False, stacklevel = 1, extra = None):
        return super().log(25, f"{Fore.GREEN}{msg}{Fore.RESET}", *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra=extra)
    def debug(self, msg, *args, exc_info = None, stack_info = False, stacklevel = 1, extra = None):
        return super().debug(f"{C["blue"]}{msg}{Fore.RESET}", *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra=extra)