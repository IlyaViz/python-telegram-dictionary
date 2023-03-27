import enum

class UserStatuses(enum.Enum):
    registration = 1
    logining = 2
    getting_word = 3
    adding_word = 4

class DbStatuses(enum.Enum):
    user_already_created = 1
    dictionary_error = 2