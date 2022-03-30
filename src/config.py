import configparser
from os import environ as env


parser = configparser.ConfigParser()
parser.read("settings.env")

try:
    APP_NAME = env["APP_NAME"]
    TOKEN = env["TOKEN"]
    MONGO_HOST = env["MONGO_HOST"]
    MONGO_USER = env["MONGO_USER"]
    MONGO_PASS = env["MONGO_PASS"]
    MONGO_BASE = env["MONGO_BASE"]
except KeyError:
    APP_NAME = parser.get("DEVELOPMENT", "APP_NAME")
    TOKEN = parser.get("DEVELOPMENT", "TOKEN")
    MONGO_HOST = parser.get("DEVELOPMENT", "MONGO_HOST")
    MONGO_USER = parser.get("DEVELOPMENT", "MONGO_USER")
    MONGO_PASS = parser.get("DEVELOPMENT", "MONGO_PASS")
    MONGO_BASE = parser.get("DEVELOPMENT", "MONGO_BASE")

PORT = int(env.get("PORT", 5000))
THUMB_URL = env.get(
    "THUMB_URL",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Ukraine.svg/2560px-Flag_of_Ukraine.svg.png",
)

REMINDER_MESSAGE = "I WILL POST PINNED MESSAGE HERE"
REMINDER_INTERVAL_PINNED = 30 * 60
REMINDER_INTERVAL_INFO = 10 * 60
PINNED_JOB = "pinned"
SOCIAL_JOB = "social"
JOBS_NAME = [PINNED_JOB, SOCIAL_JOB]
ADMIN_ONLY_CHAT_IDS = [-1001723117571, -735136184]

BERLIN_HELPS_UKRAIN_CHAT_ID = [-1001589772550, -1001790676165, -735136184]


