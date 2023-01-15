import os
import sys

DIR_NAME = "lol-announcer"

if os.name == "posix":
    if "XDG_CONFIG_HOME" in os.environ and "XDG_CACHE_HOME" in os.environ:
        LOGS_DIR = os.path.join(os.environ["XDG_CACHE_HOME"], DIR_NAME, "logs")
        SOUNDS_DIR_LOCAL = os.path.join(
            os.environ["XDG_CONFIG_HOME"], DIR_NAME, "sounds"
        )
    elif "HOME" in os.environ:
        HOME = os.environ["HOME"]
        LOGS_DIR = os.path.join(HOME, ".cache", DIR_NAME, "logs")
        SOUNDS_DIR_LOCAL = os.path.join(HOME, ".config", DIR_NAME, "sounds")
    else:
        print("HOME environment variable is not set.", file=sys.stderr)
        sys.exit(1)
elif os.name == "nt":
    if "APPDATA" in os.environ:
        APPDATA = os.environ["APPDATA"]
        LOGS_DIR = os.path.join(APPDATA, DIR_NAME, "logs")
        SOUNDS_DIR_LOCAL = os.path.join(APPDATA, DIR_NAME, "sounds")
    else:
        print("APPDATA is not set.", file=sys.stderr)
        sys.exit(1)
else:
    print("Your OS is not supported.", file=sys.stderr)
    sys.exit(1)


os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR_LOCAL, exist_ok=True)
SOUNDS_DIR_GLOBAL = os.path.join(os.path.dirname(__file__), "sounds/")


SOUND_PACKS = dict()

for dir in os.listdir(os.path.join(os.path.dirname(__file__), "sounds/")):
    SOUND_PACKS[dir] = os.path.join(os.path.dirname(__file__), "sounds/", dir)

for dir in os.listdir(SOUNDS_DIR_LOCAL):
    SOUND_PACKS[dir] = os.path.join(SOUNDS_DIR_LOCAL, dir)


LOGS_FILE = os.path.join(LOGS_DIR, "announcer.log")
LOGGING_DICT = {
    "version": 1,
    "formatters": {
        "brief": {
            "format": "[%(levelname)s] %(filename)s:%(lineno)d; %(message)s",
        },
        "precise": {
            "format": "%(asctime)s.%(msecs)03dZ %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "brief",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",
            "formatter": "precise",
            "filename": LOGS_FILE,
            "maxBytes": 32 * 1024,
            "backupCount": 3,
        },
    },
    "loggers": {
        "basicLogger": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": "no",
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],
    },
    "disable_existing_loggers": False,
}
