def authorized_required(function):
    def wrapper(update, context):
        if context.user_data.get("authorized", False):
            function(update, context)
        else:
            update.message.reply_text("You are not authorized")
    return wrapper