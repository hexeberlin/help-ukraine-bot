import configparser
from os import environ as env


parser = configparser.ConfigParser()
parser.read("settings.env")

try:
    APP_NAME = env["APP_NAME"]
    TOKEN = env["TOKEN"]
except KeyError:
    APP_NAME = parser.get("DEVELOPMENT", "APP_NAME")
    TOKEN = parser.get("DEVELOPMENT", "TOKEN")

PORT = int(env.get("PORT", 5000))

REMINDER_MESSAGE = "I WILL POST PINNED MESSAGE HERE"
REMINDER_INTERVAL_PINNED = 30 * 60
REMINDER_INTERVAL_INFO = 10 * 60
PINNED_JOB = "pinned"
SOCIAL_JOB = "social"
JOBS_NAME = [PINNED_JOB, SOCIAL_JOB]
ADMIN_ONLY_CHAT_IDS = [-1001723117571, -735136184]

BERLIN_HELPS_UKRAINE_CHAT_ID = [-1001589772550, -1001790676165, -735136184]
