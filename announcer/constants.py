import os
import sys
import json

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


def load_json_file(file_path):
    try:
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        return data
    except Exception as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
        return None


SOUND_PACKS = dict()


def process_sound_directory(sound_directory, is_global):
    for dir in os.listdir(sound_directory):
        json_file_path = os.path.join(sound_directory, dir, "config.json")

        if os.path.exists(json_file_path):
            json_data = load_json_file(json_file_path)
            if json_data is not None:
                try:
                    pack_name = json_data["name"]
                    pack_description = json_data.get("description", "")
                    pack_author = json_data.get("author", "")
                    SOUND_PACKS[pack_name] = {
                        "path": os.path.join(sound_directory, dir),
                        "description": pack_description,
                        "author": pack_author,
                    }
                except KeyError as e:
                    print(
                        f"Error in {json_file_path}: Missing key '{e}'", file=sys.stderr
                    )
            else:
                print(
                    f"Skipping sound pack in {dir} due to an error in its config.json file",
                    file=sys.stderr,
                )


process_sound_directory(SOUNDS_DIR_GLOBAL, True)
process_sound_directory(SOUNDS_DIR_LOCAL, False)

LOGS_FILE = os.path.join(LOGS_DIR, "announcer.log")
LOGGING_DICT = {
    "version": 1,
    "formatters": {
        "brief": {
            "format": "[%(levelname)s] %(filename)s:%(lineno)d; %(message)s",
        },
        "precise": {
            "format": "%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
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
        },
        "requests": {
            "level": "WARNING",
        },
        "urllib3": {
            "level": "WARNING",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],
    },
    "disable_existing_loggers": False,
}

EVENTS = [
    "PlayerFirstBlood",
    "PlayerKill",
    "PlayerDeath",
    "PlayerDeathFirstBlood",
    "Executed",
    "AllyAce",
    "AllyKill",
    "AllyDeath",
    "AllyDeathFirstBlood",
    "AllyFirstBlood",
    "AllyPentaKill",
    "AllyQuadraKill",
    "AllyTripleKill",
    "AllyDoubleKill",
    "AllyFirstBrick",
    "AllyTurretKill",
    "AllyInhibitorKill",
    "AllyInhibitorRespawned",
    "AllyInhibitorRespawningSoon",
    "AllyDragonKill",
    "AllyDragonKillStolen",
    "AllyHeraldKill",
    "AllyHeraldKillStolen",
    "AllyBaronKill",
    "AllyBaronKillStolen",
    "EnemyAce",
    "EnemyPentaKill",
    "EnemyQuadraKill",
    "EnemyTripleKill",
    "EnemyDoubleKill",
    "EnemyFirstBrick",
    "EnemyTurretKill",
    "EnemyInhibitorKill",
    "EnemyInhibitorRespawned",
    "EnemyInhibitorRespawningSoon",
    "EnemyDragonKill",
    "EnemyDragonKillStolen",
    "EnemyHeraldKill",
    "EnemyHeraldKillStolen",
    "EnemyBaronKill",
    "EnemyBaronKillStolen",
    "Victory",
    "Defeat",
    "GameStart",
    "Welcome",
    "MinionsSpawning",
    "MinionsSpawningSoon",
]
