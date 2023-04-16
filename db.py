import psycopg2
import os
import time
from classes import DbStatuses
from typing import Union

class DbConnection:
    def __init__(self):
        PASSWORD = os.environ['PG_PASSWORD']
        retry_count = 0
        while True:
            if retry_count == 3:
                raise psycopg2.OperationalError("No access to db. Check if db has started")
            
            try:
                self.connection = psycopg2.connect( host="postgres-server", 
                                                database="postgres", 
                                                user="postgres", 
                                                password=PASSWORD)
                break
            except psycopg2.OperationalError as e:
                retry_count += 1
                time.sleep(1)
  
        self.connection.autocommit = True   
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS
        users(id SERIAL PRIMARY KEY, username VARCHAR(20) unique, password VARCHAR(20));""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS
        groups(user_username VARCHAR REFERENCES users(username) NOT NULL, name VARCHAR(40) unique);""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS
        words(id SERIAL PRIMARY KEY, user_username VARCHAR REFERENCES users(username) NOT NULL, word VARCHAR(40), meaning VARCHAR(40), group_name VARCHAR REFERENCES groups(name) NOT NULL);""")

    def add_user(self, username:str, password:str) -> DbStatuses:
        try:
            self.cursor.execute(f"""INSERT INTO users(username, password)
            VALUES('{username}', '{password}');""")
            return DbStatuses.success
        except:
            return DbStatuses.user_already_created

    def is_login_successful(self, username:str, password:str) -> bool:
        try:
            self.cursor.execute(f"""SELECT * FROM users WHERE
            username='{username}' AND password='{password}';""")
            result = self.cursor.fetchone()
            return result is not None
        except:
            return False
        
    def add_group(self, username:str, group_name:str) -> DbStatuses:
        try:
            self.cursor.execute(f"""INSERT INTO groups(user_username, name)
            VALUES('{username}', '{group_name}')""")
            return DbStatuses.success
        except:
            return DbStatuses.inserting_error

    def add_word(self, username:str, word:str, meaning:str, group_name:str) -> DbStatuses:
        #check if group exists
        self.cursor.execute(f"""SELECT * FROM groups
        WHERE user_username='{username}' AND name='{group_name}';""")
        result = self.cursor.fetchone()
        if result is None:
            return DbStatuses.group_not_exist

        try:
            self.cursor.execute(f"""INSERT INTO words(user_username, word, meaning, group_name)
            VALUES('{username}', '{word}', '{meaning}', '{group_name}')""")
            return DbStatuses.success
        except:
            return DbStatuses.inserting_error
        
    def get_word(self, username:str, word:str) -> Union[str, DbStatuses]:
        #Get all words if *, otherwise get certain word; can return many meanings
        query = f"""SELECT word, meaning FROM words
        WHERE user_username='{username}'""" if word == '*' else f"""SELECT word, meaning
        FROM words WHERE user_username='{username}' AND word='{word}'"""
        self.cursor.execute(query)
        query_result = self.cursor.fetchall()
        if query_result != []:
            final_result = ""
            for row in query_result:
                final_result += ": ".join(row) + "\n"
            return final_result
        return DbStatuses.no_data

    def get_all_group_words(self, username:str, group:str) -> Union[str, DbStatuses]:
        self.cursor.execute(f"""SELECT word, meaning FROM words
        WHERE user_username='{username}' AND group_name='{group}'""")
        query_result = self.cursor.fetchall()
        if query_result != []:
            final_result = ""
            for row in query_result:
                final_result += ": ".join(row) + "\n"
            return final_result
        return DbStatuses.no_data
       

