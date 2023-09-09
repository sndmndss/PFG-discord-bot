import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

SETTINGS_PATH = Path("settings.py")
STATIC_PATH = SETTINGS_PATH.parent / ".." / "static"
DATABASE_PATH = SETTINGS_PATH.parent / ".." / "DataBases" / "guilds"

BANNER_FOLDER_ORIG = STATIC_PATH / "orig.gif"
BANNER_FOLDER_IMAGE = STATIC_PATH / "image.gif"
BANNER_LOCATION = os.getenv("BANNER_LOCATION", BANNER_FOLDER_ORIG)
EDITED_BANNER_LOCATION = os.getenv("EDITED_BANNER_LOCATION", BANNER_FOLDER_IMAGE)
DATABASE_LOCATION = os.getenv("DATABASE_LOCATION", DATABASE_PATH)
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")
LOGS_GUILD = os.getenv("LOGS_GUILD_LIST")
MICROPHONE_GUILD = os.getenv("MICROPHONE_GUILD_LIST")
COORDINATES_X = [57, 57]
COORDINATES_Y = [165, 185]
INVITES = {}
