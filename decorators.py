def authorized_required(function):
    def wrapper(update, context):
        if context.user_data.get("authorized", False):
            function(update, context)
        else:
            update.message.reply_text("You are not authorized")
    return wrapper

def unauthorized_required(function):
    def wrapper(update, context):
        if context.user_data.get("authorized", False):
            update.message.reply_text("You are already authorized")
        else:
            function(update, context)
    return wrapper