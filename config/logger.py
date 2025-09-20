import logging, sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config.settings import settings

def setup_logging():
    Path("logs").mkdir(parents=True, exist_ok=True)
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    root = logging.getLogger()
    root.setLevel(level)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    fh = RotatingFileHandler("logs/bot.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(fmt)
    root.addHandler(fh)
