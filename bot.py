import time
import telepot
from telepot.loop import MessageLoop
import subprocess
from datetime import date

rate = False # Flag for keeping track of message sequences

me = 00000000 # ID of the user comes here

def handle(msg):
    global rate
    chat_id = msg['chat']['id']
    command = msg['text']
    print('Got: ' + str(chat_id) + " " + command)
    if chat_id != me: 
        print("Got strange user")
        return
    if command == "/rate":
        bot.sendMessage(chat_id, "How well do you rate your day (1 to 10)?")
        rate = True
        return
    if rate:
        f.write('\n' + str(date.today()) + " " + msg['text'])
        rate = False

# Create a bot object with API key
bot = telepot.Bot("XXXX")

# Attach a function to notifyOnMessage call back
MessageLoop(bot, handle).run_as_thread()

# Listen to the messages
f = open("day-rating", "a")
try:
    while 1:
        time.sleep(10)
except KeyboardInterrupt:
    f.close()
