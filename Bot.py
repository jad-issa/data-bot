from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

with open("token.txt", "r") as file:
    API_TOKEN = file.readline()


def start(update, context):
    start_text = "I'm a bot, please talk to me!"
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_text)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def unknown(update, context):
    unknown_message = "Sorry, I didn't understand that command."
    context.bot.send_message(chat_id=update.effective_chat.id, text=unknown_message)


updater = Updater(token=API_TOKEN, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

caps_handler = CommandHandler('caps', caps)
dispatcher.add_handler(caps_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater.start_polling()
