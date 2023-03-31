from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from classes import UserStatuses, DbStatuses
from db import DbConnection
from decorators import authorized_required

db_connection = DbConnection()

TOKEN = "5776698149:AAEFmN4J5n3nbf8f_th8LeuYo3XMwVHoKrE"
updater = Updater(TOKEN)
dispatcher = updater.dispatcher

AVAILABLE_COMMANDS = ["register", "login", "new_word", "get_word"]

def register(update, context):
    if context.user_data.get("authorized", False):
        update.message.reply_text("Already authorized")
    else:
        update.message.reply_text("Provide data in format login:password(REGISTRATION)")
        context.user_data["status"] = UserStatuses.registration

def login(update, context):
    if username := context.user_data.get("authorized", False):
        update.message.reply_text(f"You are already logged in as {username}")
    else:
        update.message.reply_text("Provide data in format <login:password> (LOGINING)")
        context.user_data['status'] = UserStatuses.logining

@authorized_required
def new_word(update, context):
    context.user_data["status"] = UserStatuses.adding_word
    update.message.reply_text("Enter your data in format <word:word>")

@authorized_required
def get_word(update, context):
    context.user_data["status"] = UserStatuses.getting_word
    update.message.reply_text("Enter the word ( * to get all words )")

def input(update, context):
    match context.user_data.get("status", None):
        case UserStatuses.registration:
            data = update.message.text
            try:
                username, password = data.split(":")
            except:
                del context.user_data['status']
                return
            result = db_connection.add_user(username, password)
            if result == DbStatuses.user_already_created:
                update.message.reply_text("There is already user with this username")
            else:
                update.message.reply_text("Successfuly created")

        case UserStatuses.logining:
            data = update.message.text
            username, password = data.split(":")
            if db_connection.is_login_successful(username, password):
                context.user_data["authorized"] = username
                update.message.reply_text(f"Successfully authorized as {username}")
            else:
                update.message.reply_text("Invalid data")

        case UserStatuses.getting_word:
            word = update.message.text.lower()
            username = context.user_data["authorized"]
            if (result := db_connection.get_word(username, word)) == DbStatuses.dictionary_error:
                update.message.reply_text("Error. Probably there is no such word")
            else:
                for row in result:
                    data = ": ".join(row)
                    update.message.reply_text(data)

        case UserStatuses.adding_word:
            data = update.message.text
            username = context.user_data["authorized"]
            word, meaning = data.lower().split(":")
            if db_connection.add_word(username, word, meaning) == DbStatuses.dictionary_error:
                update.message.reply_text("Error")
            else:
                update.message.reply_text("Successfully added")
            
        case _:
            update.message.reply_text("What do you want: ")
            for command in AVAILABLE_COMMANDS:
                update.message.reply_text(f"/{command}")

    del context.user_data['status']


if __name__ == "__main__":
    dispatcher.add_handler(CommandHandler("register", register))
    dispatcher.add_handler(CommandHandler("login", login))
    dispatcher.add_handler(CommandHandler("new_word", new_word))
    dispatcher.add_handler(CommandHandler("get_word", get_word))
    dispatcher.add_handler(MessageHandler(Filters.text, input))

    updater.start_polling()
