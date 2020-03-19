from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

with open("token.txt", "r") as file:
    API_TOKEN = file.readline()


def start(update, context):
    start_text = "I'm a bot, please talk to me!"
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_text)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


updater = Updater(token=API_TOKEN, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater.start_polling()
