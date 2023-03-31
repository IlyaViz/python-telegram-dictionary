import psycopg2
import os
from classes import DbStatuses

class DbConnection:
    def __init__(self):
        PASSWORD = os.environ['PG_PASSWORD']
        self.connection = psycopg2.connect( host="postgres-server", 
                                            database="postgres", 
                                            user="postgres", 
                                            password=PASSWORD)
        self.connection.autocommit = True   
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS
        users(id SERIAL PRIMARY KEY, username VARCHAR(20) unique, password VARCHAR(20));""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS
        dictionary(id SERIAL PRIMARY KEY, user_username VARCHAR(20) REFERENCES users(username), word VARCHAR(40), meaning VARCHAR(40))""")

    def add_user(self, username, password):
        try:
            self.cursor.execute(f"""INSERT INTO users(username, password)
            VALUES('{username}', '{password}');""")
        except:
            return DbStatuses.user_already_created

    def is_login_successful(self, username, password):
        try:
            self.cursor.execute(f"""SELECT * FROM users WHERE
            username='{username}' AND password='{password}';""")
            result = self.cursor.fetchone()
            if len(result) != 0:
                return True
            return False
        except:
            return False
        
    def add_word(self, username, word, meaning):
        try:
            self.cursor.execute(f"""INSERT INTO dictionary(user_username, word, meaning)
            VALUES('{username}', '{word}', '{meaning}')""")
        except:
            return DbStatuses.dictionary_error
        
    def get_word(self, username, word):
        #Get all words if *, otherwise get certain word
        query = f"""SELECT word, meaning FROM dictionary
            WHERE user_username='{username}'""" if word == '*' else f"""SELECT word, meaning
            FROM dictionary WHERE user_username='{username}' AND word='{word}'"""
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            if len(result) != 0:
                return result
            return DbStatuses.dictionary_error
        except:
            return DbStatuses.dictionary_error