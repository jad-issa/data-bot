# data-bot
Telegram bot for data collection

## Goal
Collect personal data using a Telegram bot interface to be used later for analysis and statistics. The point of the bot is to be run locally and for the data to be collected locally so that no privacy issues occur

## Requirements
### Functional
- Reading a CSV file with questions and regex form of the answers (for validation)
  - If the answer is compliant with the regex provided, it should be stored
  - If the answer is not complaint, the question should be asked once again
- Writing the data, with a time stamp onto a CSV file for later analysis

Behavior is expected to be the following:

I ask `/rate` at any moment and receive a sequence of questions with a specified answer format and I reply to the questions with my answer. I might `/skip` an answer, `/cancel` the rating in which data is lost, or be `/done` with the rating prematurely in which case the available data is submitted.

### Non-functional
- Verification of the person (done via the chat id of the received message)
- Ability to dynamically add questions and have the CSV data file automatically rewritten with empty values for added columns or with the ability of deleting columns (pandas?)

## Structure
Everything is expected to reside in the root directory as follows:
```
bot.py
questions.csv
data.csv # to only be filled at runtime
```

## Contribution
You may contribute to the CSV questions file with useful questions, or contribute to `bot.py` which will do all the work.

## Running
Create a telegram bot and find it's key, then discover your ID as a user. Replace your ID in `me` in the `bot.py` and add the bot key.
