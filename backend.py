import json
import time
import pandas as pd
import csv
from openpyxl import load_workbook

class DbAct:
    def __init__(self, db, config, path_xlsx):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config
        self.__fields_pressure = ['Давление', 'Причина', 'Запись']
        self.__fields_weight = ['Вес', 'Запись']
        self.__fields_questions = ['Вопрос', 'Ответ', 'Запись']
        self.__fields_user = ['Имя', 'Фамилия', 'Никнейм']
        self.__dump_path_xlsx = path_xlsx

    def add_user(self, user_id, first_name, last_name, nick_name):
        if not self.user_is_existed(user_id):
            if user_id in self.__config.get_config()['admins']:
                is_admin = True
            else:
                is_admin = False
            self.__db.db_write(
                'INSERT INTO users (user_id, first_name, last_name, nick_name, system_data, is_admin) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, first_name, last_name, nick_name, json.dumps({"index": None,
                                                                        "pressure": None,
                                                                        "now_pressure": None,
                                                                        "remind": None,
                                                                        "pending_questions": None,
                                                                        "current_question_index": None}), is_admin))
            

    ##### СТАНДАРТНЫЕ КОМАНДЫ #####
    def user_is_existed(self, user_id: int):
        data = self.__db.db_read('SELECT count(*) FROM users WHERE user_id = ?', (user_id,))
        if len(data) > 0:
            if data[0][0] > 0:
                status = True
            else:
                status = False
            return status
        
    def user_is_admin(self, user_id: int):
        data = self.__db.db_read('SELECT is_admin FROM users WHERE user_id = ?', (user_id,))
        if len(data) > 0:
            if data[0][0] == 1:
                status = True
            else:
                status = False
            return status
        
    def set_user_system_key(self, user_id: int, key: str, value: any) -> None:
        system_data = self.get_user_system_data(user_id)
        if system_data is None:
            return None
        system_data = json.loads(system_data)
        system_data[key] = value
        self.__db.db_write('UPDATE users SET system_data = ? WHERE user_id = ?', (json.dumps(system_data), user_id))

    def get_user_system_key(self, user_id: int, key: str):
        system_data = self.get_user_system_data(user_id)
        if system_data is None:
            return None
        system_data = json.loads(system_data)
        if key not in system_data.keys():
            return None
        return system_data[key]

    def get_user_system_data(self, user_id: int):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT system_data FROM users WHERE user_id = ?', (user_id,))[0][0]
    
    #### ОСНОВНЫЕ ЗАПРОСЫ #####
    def write_user_question(self, user_id: int, question_id: int, question: str):
        self.__db.db_write('INSERT INTO user_questions (user_id, question_id, question, question_status) VALUES (?, ?, ?, True)', (user_id, question_id, question))

    def get_user_question(self, user_id: int):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT question_id, question FROM user_questions WHERE user_id = ? and question_status = True', (user_id,))
    
    def delete_user_question(self, question_id: int, user_id: int):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('UPDATE user_questions SET question_status = ? WHERE question_id = ? and user_id = ?', (False, question_id, user_id))

    def add_user_answer(self, user_id, question_id, answer):
        self.__db.db_write('UPDATE user_questions SET answer = ?, question_status = 0, created_at = CURRENT_TIMESTAMP WHERE row_id = ? AND user_id = ?', (answer, question_id, user_id))

    def get_question_by_id(self, question_id):
        result = self.__db.db_read(
            'SELECT row_id, question FROM user_questions '
            'WHERE row_id = ?',
            (question_id,)
        )
        return result[0] if result else None
    
    def question_is_exist(self, user_id: int, question_id: int):
        return self.__db.db_read('SELECT question FROM user_questions WHERE user_id = ? AND question_id = ? AND question_status = ?', (user_id, question_id, True))

    def add_user_weight(self, user_id: int, weight: int):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO user_datas (user_id, weight) VALUES (?, ?)', (user_id, weight))

    def add_user_settings(self, user_id: int, pressure: str, pills: str):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO user_settings (user_id, pressure, pills) VALUES (?, ?, ?)', (user_id, pressure, pills))

    def add_pressure_user(self, user_id: int, pressure: str, cause: str):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO user_datas (user_id, pressure, cause) VALUES (?, ?)', (user_id, pressure, cause))

    def get_user_pressure_setting(self, user_id: int):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT pressure, pills FROM user_settings WHERE user_id = ?', (user_id,))
    
    def update_user_pressure_setting(self, user_id: int, pressure: str):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('UPDATE user_settings SET pressure = ? WHERE user_id = ?', (pressure, user_id))

    def update_user_pills_setting(self, user_id: int, pills: str):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('UPDATE user_settings SET pills = ? WHERE user_id = ?', (user_id, pills))

    def add_user_remind(self, user_id: int, remind: str, time: str):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO user_reminders (user_id, reminder, at_time, is_active) VALUES (?, ?, ?, True)', (user_id, remind, int(time)))

    def get_user_remind(self, current_time):
        if current_time is None:
            current_time = int(time.time())
        res = self.__db.db_read('SELECT row_id, user_id, reminder FROM user_reminders WHERE at_time <= ? AND is_active = True', (current_time,))
        return [{'id': row[0], 'user_id': row[1], 'reminder': row[2]} for row in res]
    
    def get_today_reminders(self, user_id, start_of_day, end_of_day):
        return self.__db.db_read(
            'SELECT row_id, reminder, at_time FROM user_reminders '
            'WHERE user_id = ? AND at_time BETWEEN ? AND ? AND is_active = 1 '
            'ORDER BY at_time',
            (user_id, start_of_day, end_of_day)
        )

    def mark_reminder_as_completed(self, reminder_id: int):
        self.__db.db_write('UPDATE user_reminders SET is_active = False WHERE row_id = ?', (reminder_id,))
        
    def mark_reminder_as_unactive(self, user_id: int, question_id: int):
        self.__db.db_write('UPDATE user_reminders SET is_active = False WHERE user_id = ? AND row_id = ?', (user_id, question_id,))

    def get_user_remind_by_userid(self, user_id: int):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT row_id, reminder, at_time FROM user_reminders WHERE user_id = ? AND is_active = True', (user_id,))
    
    def reminder_is_exist(self, user_id: int, remind_id: int):
        return self.__db.db_read('SELECT row_id, reminder FROM user_reminders WHERE user_id = ? AND is_active = True AND row_id = ?', (user_id, remind_id,))
    
    def get_pressure_report(self, user_id: int):
        try:
            data = {'Давление': [], 'Причина': [], 'Запись': []}
            pressures_data = self.__db.db_read('SELECT pressure, cause, created_at FROM user_datas WHERE user_id = ? AND pressure IS NOT NULL', (user_id,))
            if len(pressures_data) > 0:
                for pressure in pressures_data:
                    for info in range(len(list(pressure))):
                        data[self.__fields_pressure[info]].append(pressure[info])
                df = pd.DataFrame(data)
                df.to_excel(self.__config.get_config()['xlsx_path'], sheet_name='Давление', index=False)
        except Exception as e:
            return None
                
    def get_weight_report(self, user_id: int):
        try:  
            data = {'Вес': [], 'Запись': []}
            weight_data = self.__db.db_read('SELECT weight, created_at FROM user_datas WHERE user_id = ? AND weight IS NOT NULL', (user_id,))
            if len(weight_data) > 0:
                for weight in weight_data:
                    for info in range(len(list(weight))):
                        data[self.__fields_weight[info]].append(weight[info])
                df = pd.DataFrame(data)
                df.to_excel(self.__config.get_config()['xlsx_path'], sheet_name='Вес', index=False)
        except Exception as e:  
            return None

    def get_question_answer_report(self, user_id: int):
        try:
            data = {'Вопрос': [], 'Ответ': [], 'Запись': []}
            question_answer_data = self.__db.db_read('SELECT question, answer, created_at FROM user_questions WHERE user_id = ?', (user_id,))
            if len(question_answer_data) > 0:
                for question_answer in question_answer_data:
                    for info in range(len(list(question_answer))):
                        data[self.__fields_questions[info]].append(question_answer[info])
                df = pd.DataFrame(data)
                df.to_excel(self.__config.get_config()['xlsx_path'], sheet_name='Вопросы и ответы', index=False)
        except Exception as e:
            return None
        
    def db_export_xlsx(self):
        try:
            d = {'Имя': [], 'Фамилия': [], 'Никнейм': []}
            users = self.__db.db_read('SELECT first_name, last_name, nick_name FROM users', ())
            if len(users) > 0:
                for user in users:
                    for info in range(len(list(user))):
                        d[self.__fields_user[info]].append(user[info])
                df = pd.DataFrame(d)
                df.to_excel(self.__config.get_config()['xlsx_path'], sheet_name='Пользователи', index=False)
        except Exception as e:
            return None
