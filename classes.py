import enum

class UserStatuses(enum.Enum):
    registration = 0
    logining = 1
    adding_group = 2
    adding_word = 3
    getting_word = 4
    getting_all_group_words = 5

class DbStatuses(enum.Enum):
    success = 0
    no_data = 1
    user_already_created = 2
    inserting_error = 3
    group_not_exist = 4
    blank_list = 5
    
    
    @property
    def description(self):
        descriptions = {DbStatuses.success:"Success",
                        DbStatuses.no_data:"This data wasn't found. Check if input data exists and has something inside",
                        DbStatuses.user_already_created:"Seems that user was already created",
                        DbStatuses.inserting_error:"Something went wrong. Common reasons: word is too long or something(word, group) already exists",
                        DbStatuses.group_not_exist:"There is no such group",
                        DbStatuses.blank_list:"The result is empty"}
        return descriptions[self]
