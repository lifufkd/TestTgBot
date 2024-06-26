#####################################
#            Created by             #
#                SBR                #
#####################################
import os
import sqlite3
#####################################


class DB:
    def __init__(self, path, lock):
        super(DB, self).__init__()
        self.__lock = lock
        self.__db_path = path
        self.__cursor = None
        self.__db = None
        self.init()

    def init(self):
        if not os.path.exists(self.__db_path):
            self.__db = sqlite3.connect(self.__db_path, check_same_thread=False)
            self.__cursor = self.__db.cursor()
            self.__cursor.execute('''
            CREATE TABLE users(
            row_id INTEGER primary key autoincrement not null,
            user_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            nick_name TEXT,
            is_admin BOOL,
            UNIQUE(user_id)
            )
            ''')
            self.__cursor.execute('''
            CREATE TABLE tests(
            row_id INTEGER,
            name TEXT,
            test_command TEXT,
            description TEXT,
            text_start_btn TEXT,
            text_continue_btn TEXT,
            before_test TEXT,
            after_question_c TEXT,
            after_question_i TEXT,
            after_test TEXT,
            correct_link BLOB,
            incorrect_link BLOB,
            row_width TEXT,
            questions TEXT,
            start_question TEXT,
            start_answer TEXT,
            again_test_btn TEXT,
            new_test_btn TEXT
            )
            ''')
            self.__cursor.execute('''
            CREATE TABLE questions(
            row_id TEXT,
            name TEXT,
            questions TEXT,
            answer_description TEXT,
            correct INTEGER,
            id_test TEXT
            )
            ''')
            self.__cursor.execute('''
            CREATE TABLE statistic(
            row_id INTEGER primary key autoincrement not null,
            test_name TEXT,
            date INTEGER,
            progress INTEGER, 
            marks INTEGER,
            user_nick TEXT
            )
            ''')
            self.__db.commit()
        else:
            self.__db = sqlite3.connect(self.__db_path, check_same_thread=False)
            self.__cursor = self.__db.cursor()

    def db_write(self, queri, args):
        self.set_lock()
        self.__cursor.execute(queri, args)
        self.__db.commit()
        self.realise_lock()

    def db_read(self, queri, args):
        self.set_lock()
        self.__cursor.execute(queri, args)
        self.realise_lock()
        return self.__cursor.fetchall()

    def set_lock(self):
        self.__lock.acquire(True)

    def realise_lock(self):
        self.__lock.release()
