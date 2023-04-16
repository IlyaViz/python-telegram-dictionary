from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from classes import UserStatuses, DbStatuses
from db import DbConnection
from decorators import authorized_required, unauthorized_required

db_connection = DbConnection()

TOKEN = "5776698149:AAEFmN4J5n3nbf8f_th8LeuYo3XMwVHoKrE"
updater = Updater(TOKEN)
dispatcher = updater.dispatcher

AVAILABLE_COMMANDS = ["register", "login", "add_group", "add_word", "get_word", "get_all_group_words", "get_all_groups"]

@unauthorized_required
def register(update, context):
    update.message.reply_text("Provide data in format login:password (registartion)")
    context.user_data["status"] = UserStatuses.registration

@unauthorized_required
def login(update, context):
    update.message.reply_text("Provide data in format <login:password> (logining)")
    context.user_data['status'] = UserStatuses.logining

@authorized_required
def add_group(update, context):
    context.user_data["status"] = UserStatuses.adding_group
    update.message.reply_text("Enter the group name")

@authorized_required
def add_word(update, context):
    context.user_data["status"] = UserStatuses.adding_word
    update.message.reply_text("Enter your data in format <word:meaning:group>")

@authorized_required
def get_word(update, context):
    context.user_data["status"] = UserStatuses.getting_word
    update.message.reply_text("Enter the word ( * to get_word all words )")

@authorized_required
def get_all_group_words(update, context):
    context.user_data["status"] = UserStatuses.getting_all_group_words
    update.message.reply_text("Enter the group name")

@authorized_required
def get_all_groups(update, context):
    username = context.user_data["authorized"]
    result = db_connection.get_all_groups(username)
    if isinstance(result, str):
        update.message.reply_text(result)
    else:
        update.message.reply_text(result.description)

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
            try:
                username, password = data.split(":")
            except:
                del context.user_data['status']
                return
            if db_connection.is_login_successful(username, password):
                context.user_data["authorized"] = username
                update.message.reply_text(f"Successfully authorized as {username}")
            else:
                update.message.reply_text("Invalid data")

        case UserStatuses.adding_group:
            data = update.message.text
            username = context.user_data["authorized"]
            result = db_connection.add_group(username, data)
            update.message.reply_text(result.description)

        case UserStatuses.adding_word:
        #add only lowercase words
            data = update.message.text
            username = context.user_data["authorized"]
            try:
                word, meaning, group_name = data.split(":")
                # words and meaning should be lowercase; group_name should be standart case
                word, meaning = word.lower(), meaning.lower()
                result = db_connection.add_word(username, word, meaning, group_name)
                update.message.reply_text(result.description)
            except:
                update.message.reply_text('Bad format')
    
        case UserStatuses.getting_word:
            #lower the word to find it in all words(all words are lowercase)
            word = update.message.text.lower()
            username = context.user_data["authorized"]
            result = db_connection.get_word(username, word)
            if isinstance(result, str):
                update.message.reply_text(result)
            else:
                update.message.reply_text(result.description)
            
        case UserStatuses.getting_all_group_words:
            data = update.message.text
            username = context.user_data["authorized"]
            result = db_connection.get_all_group_words(username, data)
            if isinstance(result, str):
                update.message.reply_text(result)
            else:
                update.message.reply_text(result.description)
            
        case None:
            update.message.reply_text("What do you want: ")
            for command in AVAILABLE_COMMANDS:
                update.message.reply_text(f"/{command}")

    if context.user_data.get('status', False):
        del context.user_data['status']


if __name__ == "__main__":
    dispatcher.add_handler(CommandHandler("register", register))
    dispatcher.add_handler(CommandHandler("login", login))
    dispatcher.add_handler(CommandHandler("add_group", add_group))
    dispatcher.add_handler(CommandHandler("add_word", add_word))
    dispatcher.add_handler(CommandHandler("get_word", get_word))
    dispatcher.add_handler(CommandHandler("get_all_group_words", get_all_group_words))
    dispatcher.add_handler(CommandHandler("get_all_groups", get_all_groups))
    dispatcher.add_handler(MessageHandler(Filters.text, input))

    updater.start_polling()
