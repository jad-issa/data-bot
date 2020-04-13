from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler,
                          MessageHandler, ConversationHandler, Filters)
import json
import time
import logging
import os.path


# Setting up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Config
# NOTE: when changing these, keep in mind to take a look at the .gitignore
config_filename = "config.json"
questions_filename = "questions.json"
data_filename = "data.csv"

# Enums
ANSWER, COMPLETED = 0, 1


def get_config(filename):
    if not os.path.exists(filename) and not os.path.isfile(filename):
        logger.error("FATAL: No token file found. Cannot launch bot without bot token")
        raise Exception
    else:
        logger.info("Opening configuration file as JSON.")
        with open(filename, "r") as file:
            config = json.load(file)
            logger.info("Successfully opened the configuration file.")

            try:
                logger.debug("Reading bot token.")
                API_TOKEN = config["bot_token"]
                logger.info("Successfully read bot token.")
            except KeyError:
                logger.error("FATAL: No token found in configuration file.")
                raise Exception

            try:
                logger.debug("Attempting to read the authorized chat ID.")
                AUTHORIZED_CHAT = config["authorized_id"]
                logger.info("Successfully read the authorized chat(s) ID.")
            except KeyError:
                logger.error("No authorized chat ID found. Continuing without chat fitering.")
                AUTHORIZED_CHAT = None

    return API_TOKEN, AUTHORIZED_CHAT


def get_questions(filename):
    # Reading the questions from the questions file (JSON)
    if not os.path.exists(filename) and not os.path.isfile(filename):
        logger.warning("No questions file found. Cannot ask questions without questions file")
        questions=[]
    else:
        with open(filename, "r") as read_file:
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

    return list(filter(lambda x: x["used"], questions))


def add_answer(value, answers=[]):
    """
    Adds the last recorded answer
    """
    ID, *answer = value.split(",")
    answer = ",".join(answer).strip()
    row = ID + "," + str(int(time.time())) + ',"' + answer + '",\n'
    answers.append(row)
    return answers


def init_data_file(filename):
    """
    Initializes the CSV data file if non-existant with a header
    """
    if not os.path.exists(filename) and not os.path.isfile(filename):
        logger.info("Data file not found. Creating instead...")
        try:
            with open(filename, "w") as file:
                headers = "QuestionId, Timestamp, Answer,\n"
                file.write(headers)
            logger.info("Data file succesfully created.")
        except Exception as e:
            logger.error("FATAL: Could not create data file due to the following exception:")
            logger.debug(e)
            raise e
    else:
        logger.info("Found data file.")


def save_to_file(answers, filename):
    """
    Save the answers to the data file. Stores as CSV.
    """
    logger.info("Attempting to save recorded answers to file " + filename)
    try:
        with open(filename, "a") as file:
            for answer in answers:
                file.write(answer)
    except Exception as e:
        logger.error("Could not save recorded answers to file.")
        logger.debug(e)
        raise e


def ask_question(question, update, context):
    logger.debug("Beginning preparation of keyboard for question " + str(questions[0]["id"]))

    # Setup inline keyboard layout for question
    current_character_number = 0
    current_row = []
    keyboard = []

    for value in question["values"]:
        current_character_number += len(value)
        current_row.append(InlineKeyboardButton(value,
                           callback_data=str(question["id"]) + ',' + value))

        if current_character_number > 20:
            keyboard.append(current_row)
            current_row = []
            current_character_number = 0

    if len(current_row) != 0:
        keyboard.append(current_row)
        current_row = []
        current_character_number = 0

    reply_markup = InlineKeyboardMarkup(keyboard)
    logger.debug("Keyboard ready for question " + str(question["id"]))

    # Ask the question
    context.bot.send_message(chat_id=update.effective_chat.id, text=question["content"], reply_markup=reply_markup)

    logger.info("Question id " + str(question["id"]) +
                " sent to user " + str(update.effective_chat.id))


def completed_questions(update, context):
    logger.info("Received text while awaiting confirmation for recorded answers.")
    context.bot.send_message(chat_id=update.effective_chat.id, 
        text="Type /done to record your answers or /cancel to discard them")
    return COMPLETED


def start(update, context):
    start_text = "I'm a bot, please talk to me!"
    logger.info("Received /start command from user " + str(update.effective_chat.id))
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_text)
    logger.info("/start reply sent to user " + str(update.effective_chat.id))


def echo(update, context):
    logger.info("Received textual message from user " + str(update.effective_chat.id))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=update.message.text)

    logger.info("echo sent back to user " + str(update.effective_chat.id))


def ask(update, context):
    global current_question_index
    current_question_index = 0
    global current_answers
    current_answers = []

    logger.info("Received /ask command from user " + str(update.effective_chat.id))
    ask_question(questions[current_question_index], update, context)

    return ANSWER


def undo(update, context):
    global current_question_index
    current_question_index -= 1

    logger.info("Received /undo command from user " + str(update.effective_chat.id))
    if current_answers:
        current_answers.pop()
        logger.info("Successfully deleted last record answer.")
    else:
        current_question_index = 0
        logger.warning("Cannot delete answer from empty list. Proceeding")

    ask_question(questions[current_question_index], update, context)
    return ANSWER


def skip(update, context):
    global current_question_index

    logger.info("Received /skip command from user " + str(update.effective_chat.id))
    if current_question_index == len(questions) - 1:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Completed questions for now.")

        completed_questions(update, context)
    else:
        current_question_index += 1
        ask_question(questions[current_question_index], update, context)
        return ANSWER


def done(update, context):
    logger.info("Received /done command from user " + str(update.effective_chat.id))
    logger.info("Attempting to save recorded answers to file " + data_filename)
    save_to_file(current_answers, data_filename)
    logger.info("Successfully saved answers to file.")
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Answers succesfully recorded.")
    return ConversationHandler.END


def cancel(update, context):
    logger.info("Received /cancel request, exiting without saving answers.")
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Answers discarded.")
    return ConversationHandler.END


def answer(update, context):
    global current_question_index
    global current_answers

    logger.info("Received /answer command from user " + str(update.effective_chat.id))

    query = update.callback_query
    # query.edit_message_text(text="Selected option: {}".format(query.data.split(",")[1]))
    message = query.message.text
    answer = ",".join(query.data.split(",")[1:])
    query.edit_message_text(text=message + "\n" + answer)

    logger.info("Answer to question " + str(query.data.split(",")[0]) +
                " received from user " + str(update.effective_chat.id))

    current_answers = add_answer(query.data, current_answers)

    current_question_index += 1

    if current_question_index == len(questions):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Completed questions for now. Press /done to save or /cancel to discard")

        logger.info("Completed all questions. Awaiting confirmation.")
        return COMPLETED
    else:
        ask_question(questions[current_question_index], update, context)
        return ANSWER


def button(update, context):
    query = update.callback_query

    ID, _ = query.data.split(",")
    logger.info("Answer to question " + str(ID) + " received from user " +
                str(update.effective_chat.id))

    query.edit_message_text(text="Selected option: {}".format(query.data))
    logger.info("Answer to question " + str(ID) + " registered")


def unknown(update, context):
    unknown_message = "Sorry, I didn't understand that command."
    logger.info("Unknown command received from user " +
                str(update.effective_chat.id))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=unknown_message)


def main():
    global questions
    questions = get_questions(questions_filename)
    global current_question_index
    current_question_index = 0

    init_data_file(data_filename)

    API_TOKEN, AUTHORIZED_CHAT = get_config(config_filename)
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # If chat filtering is enabled AUTHORIZED_CHAT will be int or List[int]
    if AUTHORIZED_CHAT:
        ask_handler = CommandHandler('ask', ask, filters=Filters.chat(AUTHORIZED_CHAT))
    else:
        ask_handler = CommandHandler('ask', ask)

    conv_handler = ConversationHandler(
            entry_points=[ask_handler],

            states={
                ANSWER: [CallbackQueryHandler(answer),
                         CommandHandler('skip', skip),
                         CommandHandler('undo', undo)],
                COMPLETED: [MessageHandler(Filters.text & ~ Filters.command, completed_questions),
                            CommandHandler('undo', undo)],
            },

            fallbacks=[CommandHandler('done', done),
                       CommandHandler('cancel', cancel)]
        )

    dispatcher.add_handler(conv_handler)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)

    updater.start_polling()


main()
