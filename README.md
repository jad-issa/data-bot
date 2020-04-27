# data-bot
Telegram bot for data collection

## Goal
Collect personal data using a Telegram bot interface to be used later for analysis and statistics. The point of the bot is to be run locally and for the data to be collected locally so that no privacy issues occur.

## Usage
The following commands are supported:

- /start - test command to ping the bot or get your ID
- /ask - get a survey to answer -- only works for the authorized ID
- /undo - within the survey, undo last answer
- /skip - within the survey, skip current question
- /cancel - discard all answers of the current survey
- /done - save all answers of the survey in the data file
- Any text: will reply with that same text (similar in use to /start)

## Get started
1. Create a Telegram bot and get the token for it
2. Setup `config.json`
  - Create the file
  - Add your bot token (see 'Configuration')
3. Run the bot with `python Bot.py`
4. Find your personal ID on Telegram. This is a number unique to your user. You can find it in whichever way you want, but contacting this bot while it's running will output to the console your ID.
5. Adjust `config.json` (see 'Configuration')
6. Adjust `questions.json` (see 'Configuration')
7. Stop your program and run it anew (see 'Usage')
8. Optionally set (with `BotFather`) the commands for your bot, a name, and a profile picture

## Directory structure
```
data-bot
  Bot.py - the actual program to be run
  config.json - configuration
  questions.json - question list
  data.csv - answers (automatically create)
```

## Configuration
Configuration is primarily in the `config.json` file and is under this format:
```
{
  "bot_token": your_token_here,
  "authorized_id": your_id_here
}
```
but some configuration also leaks into the `questions.json` file where it every question is either enabled or disabled.
You can get your bot token by following the instructions [here](https://core.telegram.org/bots#6-botfather).

## Questions format
The `questions.json` is a JSON list of questions, each of which is under this format:
```
{
    "id": unique id never to be changed (AT ALL),
    "used": boolean indicating whether or not the question is to be asked (configuration),
    "content": the question string supposed to be read by the user,
    "values": STRING list of the possible answer values
}
```

## Data format
The data file is a CSV file where each row is an answer and the columns are: 

- `QuestionId` refers to the ID of the question for which this is the answer
- `Timestamp` time-stamp (Unix time) of the answer (to be used for stats and correlations)
- `Answer` the actual answer inside a string (with quotations)

## Contribution
You may contribute to the JSON questions file with useful questions, but do not activate them and make sure not to delete any previous question and add a new, distinct ID for your questions. You may also contribute to `Bot.py` directly which will do all the work.
