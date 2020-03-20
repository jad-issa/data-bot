from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import json
import time
import logging

with open("token.txt", "r") as file:
    API_TOKEN = file.readline()

# Reading the questions from the data file
with open("questions.json", "r") as read_file:
    questions = json.load(read_file)


def save_to_file(value):
    ID, *answer = value.split(",")
    answer = ",".join(answer).strip()
    row = ID + "," + str(int(time.time())) + ',"' + answer + '",'
    with open("data.csv", "a") as file:
        file.write(row)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


logger = logging.getLogger(__name__)


def start(update, context):
    start_text = "I'm a bot, please talk to me!"
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_text)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def ask(update, context):
    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')],

                [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query
    query.edit_message_text(text="Selected option: {}".format(query.data))
    

def unknown(update, context):
    unknown_message = "Sorry, I didn't understand that command."
    context.bot.send_message(chat_id=update.effective_chat.id, text=unknown_message)


updater = Updater(token=API_TOKEN, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

caps_handler = CommandHandler('caps', caps)
dispatcher.add_handler(caps_handler)

ask_handler = CommandHandler('ask', ask)
dispatcher.add_handler(ask_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

callback_handler = CallbackQueryHandler(button)
updater.dispatcher.add_handler(callback_handler)

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
