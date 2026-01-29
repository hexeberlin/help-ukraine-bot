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
