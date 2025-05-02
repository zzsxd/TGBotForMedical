import os
import sqlite3


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
            CREATE TABLE IF NOT EXISTS users(
                row_id INTEGER primary key autoincrement not null,
                user_id INTEGER NOT NULL,
                first_name TEXT,
                last_name TEXT,
                nick_name TEXT,
                is_admin BOOL,
                system_data TEXT,
                UNIQUE(user_id)
                )
            ''')
            self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_questions(
                row_id INTEGER primary key autoincrement not null,
                user_id INTEGER NOT NULL,
                question_id INTEGER,
                question_status BOOL,
                question TEXT,
                answer TEXT,
                created_at TIMESTAMP DEFAULT NULL,
                UNIQUE(row_id)
                )
            ''')
            self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_datas(
                row_id INTEGER primary key autoincrement NOT NULL,
                user_id INTEGER NOT NULL,
                pressure TEXT,
                cause TEXT,
                weight INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(row_id)
                )
            ''')
            self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_reminders(
                row_id INTEGER primary key autoincrement not null,
                user_id INTEGER NOT NULL,
                reminder TEXT,
                is_active BOOL,
                base_time INTEGER NOT NULL,
                next_time INTEGER NOT NULL,
                repeat_type TEXT NOT NULL, 
                custom_days TEXT,  
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(row_id)
              )
            ''')
            self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings(
                row_id INTEGER primary key autoincrement not null,
                user_id INTEGER NOT NULL,
                pressure TEXT,
                pills TEXT,
                UNIQUE(user_id)
                )
            ''')
            self.__db.commit()
        else:
            self.__db = sqlite3.connect(self.__db_path, check_same_thread=False)
            self.__cursor = self.__db.cursor()

    def db_write(self, queri, args):
        self.set_lock()
        self.__cursor.execute(queri, args)
        status = self.__cursor.lastrowid
        self.__db.commit()
        self.realise_lock()
        return status

    def db_read(self, queri, args):
        self.set_lock()
        self.__cursor.execute(queri, args)
        self.realise_lock()
        return self.__cursor.fetchall()

    def set_lock(self):
        self.__lock.acquire(True)

    def realise_lock(self):
        self.__lock.release()