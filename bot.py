from telegram.ext import Updater
import logging

with open("token.txt") as file:
    API_TOKEN = file.readline()

updater = Updater(token=API_TOKEN, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
