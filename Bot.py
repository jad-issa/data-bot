from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import json
import time
import logging
import os.path


# Setting up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)

# Config
# NOTE: when changing these, keep in mind to take a look at the .gitignore
token_filename = "token.txt"
questions_filename = "questions.json"
data_filename = "data.csv"

# Reading token from token file
if not os.path.exists(token_filename) and not os.path.isfile(token_filename):
    logger.error("FATAL: No token file found. Cannot launch bot without bot token")
    raise Exception
else:
    with open(token_filename, "r") as file:
        API_TOKEN = file.readline()
        logger.debug("Read token from token file")

# Reading the questions from the questions file (JSON)
if not os.path.exists(token_filename) and not os.path.isfile(questions_filename):
    logger.warning("No questions file found. Cannot ask questions without questions file")
    questions=[]
else:
    with open(questions_filename, "r") as read_file:
        logger.debug("Loading question file as JSON")
        try:
            questions = json.load(read_file)
            logger.debug("Question file loaded as JSON")
        except Exception as e:
            logger.warning("Questions file was not read successfully as JSON;" 
                           "please check questions file")
            logger.debug("Questions file unsuccessfully loaded as JSON;"
                         "setting questions variable as empty instead and continuing")
            questions = []
            logger.debug(e)


def init_data_file():
    """
    Initializes the CSV data file if non-existant with a header
    """
    if not os.path.exists(data_filename) and not os.path.isfile(data_filename):
        logger.info("Data file not found. Creating instead...")
        try:
            with open(data_filename, "w") as file:
                headers = "QuestionId, Timestamp, Answer,"
                file.write(headers)
            logger.info("Data file succesfully created.")
        except Exception as e:
            logger.error("FATAL: Could not create data file due to the following exception:")
            logger.debug(e)
            raise e
    else:
        logger.info("Found data file.")


def save_to_file(value):
    """
    Save an answer to the data file. Stores as CSV.
    """
    ID, *answer = value.split(",")
    answer = ",".join(answer).strip()
    row = ID + "," + str(int(time.time())) + ',"' + answer + '",'
    with open(data_filename, "a") as file:
        file.write(row)


def start(update, context):
    start_text = "I'm a bot, please talk to me!"
    logger.info("Received /start command from user " + str(update.effective_chat.id))
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_text)
    logger.info("/start reply sent to user " + str(update.effective_chat.id))


def echo(update, context):
    logger.info("Received textual message from user " + str(update.effective_chat.id))
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
    logger.info("echo sent back to user " + str(update.effective_chat.id))


def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    logger.info("Received /caps command from user " + str(update.effective_chat.id))
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)
    logger.info("/caps reply sent to user " + str(update.effective_chat.id))


def ask(update, context):
    logger.info("Received /ask command from user " + str(update.effective_chat.id))
    logger.debug("Beginning preparation of keyboard for question " + str(questions[0]["id"]))

    # Setup inline keyboard layout for question
    current_character_number = 0
    current_row = []
    keyboard = []

    for value in questions[0]["values"]:
        current_character_number += len(value)
        current_row.append(InlineKeyboardButton(value,
                        callback_data=str(questions[0]["id"]) + ',' + value))

        if current_character_number > 20:
            keyboard.append(current_row)
            current_row = []
            current_character_number = 0

    if len(current_row) != 0:
        keyboard.append(current_row)
        current_row = []
        current_character_number = 0

    reply_markup = InlineKeyboardMarkup(keyboard)
    logger.debug("Keyboard ready for question " + str(questions[0]["id"]))

    # Ask the question
    update.message.reply_text(questions[0]["content"], reply_markup=reply_markup)
    logger.info("Question id " + str(questions[0]["id"]) + " sent to user " +
            str(update.effective_chat.id))


def button(update, context):
    query = update.callback_query

    ID, _ = query.data.split(",")
    logger.info("Answer to question " + str(ID) + " received from user " +
            str(update.effective_chat.id))

    query.edit_message_text(text="Selected option: {}".format(query.data))
    logger.info("Answer to question " + str(ID) + " registered")


def unknown(update, context):
    unknown_message = "Sorry, I didn't understand that command."
    logger.info("Unknown command received from user " + str(update.effective_chat.id))
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

init_data_file()
updater.start_polling()
