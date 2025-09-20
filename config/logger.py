import logging
import sys
from logging.handlers import TimedRotatingFileHandler

# Настройка логирования
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Формат логов
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    "%Y-%m-%d %H:%M:%S"
)

# Лог в консоль
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Лог в файл (ротация каждую минуту, хранить 10 файлов)
file_handler = TimedRotatingFileHandler(
    "bot.log",
    when="M",             # "M" = минуты
    interval=1,           # шаг = 1 минута
    backupCount=10,       # хранить максимум 10 логов
    encoding="utf-8",
    delay=False
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

__all__ = ["logger"]
