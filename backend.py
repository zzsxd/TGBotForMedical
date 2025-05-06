import json
import time
import pandas as pd
import csv
from openpyxl import load_workbook
from datetime import datetime, timedelta

class DbAct:
    def __init__(self, db, config, path_xlsx):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config
        self.__fields_pressure = ['Давление', 'Причина', 'Запись']
        self.__fields_weight = ['Вес', 'Запись']
        self.__fields_questions = ['Вопрос', 'Ответ', 'Последняя запись']
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
                                                                        "time_remind": None,
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
        # Получаем максимальный ID вопроса для данного пользователя
        max_id = self.__db.db_read(
            'SELECT MAX(question_id) FROM user_questions WHERE user_id = ?',
            (user_id,)
        )[0][0]
        
        # Если это первый вопрос, устанавливаем ID = 1
        if max_id is None:
            new_id = 1
        else:
            # Иначе берем следующий ID
            new_id = max_id + 1
        
        # Вставляем вопрос с новым ID
        self.__db.db_write(
            'INSERT INTO user_questions (user_id, question_id, question, question_status) VALUES (?, ?, ?, True)',
            (user_id, new_id, question)
        )

    def get_user_question(self, user_id: int):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT question_id, question FROM user_questions WHERE user_id = ? and question_status = True', (user_id,))
    
    def delete_user_question(self, question_id: int, user_id: int):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('UPDATE user_questions SET question_status = ? WHERE question_id = ? and user_id = ?', (False, question_id, user_id))
    
    def add_user_answer(self, user_id, question_id, answer):
        # Получаем текущий ответ
        current_answer = self.__db.db_read('''
            SELECT answer FROM user_questions 
            WHERE row_id = ? AND user_id = ?
        ''', (question_id, user_id))
        
        # Формируем новый ответ
        new_answer = answer
        if current_answer and current_answer[0][0]:
            new_answer = f"{current_answer[0][0]}|{answer}"
        
        # Обновляем поле
        self.__db.db_write('''
            UPDATE user_questions 
            SET answer = ?, created_at = CURRENT_TIMESTAMP 
            WHERE row_id = ? AND user_id = ?
        ''', (new_answer, question_id, user_id))

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
        self.__db.db_write('INSERT INTO user_datas (user_id, pressure, cause) VALUES (?, ?, ?)', (user_id, pressure, cause))

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
        self.__db.db_write('INSERT INTO user_reminders (user_id, reminder, base_time, is_active) VALUES (?, ?, ?, True)', (user_id, remind, int(time)))

    def add_reminder(self, user_id: int, remind: str, base_time: int, repeat_type: str, custom_days: str = None):
        if not self.user_is_existed(user_id):
            return None
        
        # Получаем часовой пояс пользователя
        user_timezone = self.get_user_timezone(user_id)
        if not user_timezone:
            user_timezone = 'UTC'
            
        try:
            import pytz
            from datetime import datetime, timezone as tz, timedelta
            user_tz = pytz.timezone(user_timezone)
            
            # Конвертируем время в часовой пояс пользователя
            base_dt = datetime.fromtimestamp(base_time, tz=tz.utc).astimezone(user_tz)
            
            # Для разовых напоминаний next_time равен base_time
            if repeat_type == 'no_repeat':
                next_time = base_time
            else:
                # Для повторяющихся напоминаний next_time равен base_time
                # (они будут обновляться при отправке)
                next_time = base_time
            
            return self.__db.db_write(
                'INSERT INTO user_reminders (user_id, reminder, base_time, next_time, is_active, repeat_type, custom_days, timezone) '
                'VALUES (?, ?, ?, ?, True, ?, ?, ?)',
                (user_id, remind, base_time, next_time, repeat_type, custom_days, user_timezone)
            )
        except Exception as e:
            print(f"Ошибка при добавлении напоминания: {e}")
            return None

    def get_user_remind(self, current_time):
        if current_time is None:
            current_time = int(time.time())
        
        # Получаем все активные напоминания
        res = self.__db.db_read(
            'SELECT r.row_id, r.user_id, r.reminder, r.repeat_type, r.custom_days, r.base_time, r.next_time, r.timezone '
            'FROM user_reminders r '
            'WHERE r.is_active = True',
            ()
        )
        
        reminders = []
        for row in res:
            reminder_id, user_id, reminder, repeat_type, custom_days, base_time, next_time, timezone = row
            
            try:
                from datetime import datetime, timezone as tz, timedelta
                import pytz
                user_tz = pytz.timezone(timezone)
                
                # Конвертируем текущее время в часовой пояс пользователя
                current_time_user = datetime.fromtimestamp(current_time, tz=tz.utc).astimezone(user_tz)
                
                # Конвертируем время напоминания в часовой пояс пользователя
                remind_time = datetime.fromtimestamp(next_time, tz=tz.utc).astimezone(user_tz)
                
                # Проверяем, нужно ли отправить напоминание в текущем часовом поясе
                if remind_time <= current_time_user:
                    # Если это разовое напоминание, деактивируем его
                    if repeat_type == 'no_repeat':
                        self.mark_reminder_as_completed(reminder_id)
                    else:
                        # Для повторяющихся напоминаний обновляем next_time
                        base_dt = datetime.fromtimestamp(base_time, tz=tz.utc).astimezone(user_tz)
                        
                        if repeat_type == 'daily':
                            # Устанавливаем на завтра в то же время
                            next_time_dt = current_time_user.replace(
                                hour=base_dt.hour,
                                minute=base_dt.minute,
                                second=0,
                                microsecond=0
                            ) + timedelta(days=1)
                        elif repeat_type == 'weekly':
                            # Устанавливаем на следующую неделю в тот же день и время
                            next_time_dt = current_time_user.replace(
                                hour=base_dt.hour,
                                minute=base_dt.minute,
                                second=0,
                                microsecond=0
                            ) + timedelta(weeks=1)
                        elif repeat_type == 'monthly':
                            # Устанавливаем на следующий месяц в тот же день и время
                            next_time_dt = current_time_user.replace(
                                hour=base_dt.hour,
                                minute=base_dt.minute,
                                second=0,
                                microsecond=0
                            ) + timedelta(days=30)
                        elif repeat_type == 'custom' and custom_days:
                            # Для пользовательских дней находим следующий день из списка
                            current_day = current_time_user.weekday() + 1
                            custom_days_list = [int(d) for d in custom_days.split(',')]
                            next_day = min([d for d in custom_days_list if d > current_day], default=custom_days_list[0])
                            days_to_add = (next_day - current_day) % 7
                            
                            next_time_dt = current_time_user.replace(
                                hour=base_dt.hour,
                                minute=base_dt.minute,
                                second=0,
                                microsecond=0
                            ) + timedelta(days=days_to_add)
                        
                        # Конвертируем обратно в UTC
                        new_next_time = int(next_time_dt.astimezone(tz.utc).timestamp())
                        
                        # Обновляем next_time в базе данных
                        self.__db.db_write(
                            'UPDATE user_reminders SET next_time = ? WHERE row_id = ?',
                            (new_next_time, reminder_id)
                        )
                    
                    reminders.append({
                        'id': reminder_id,
                        'user_id': user_id,
                        'reminder': reminder
                    })
                
            except Exception as e:
                continue
        
        return reminders
    
    def get_today_reminders(self, user_id, start_of_day, end_of_day):
        # Получаем часовой пояс пользователя
        user_timezone = self.get_user_timezone(user_id)
        if not user_timezone:
            user_timezone = 'UTC'
            
        try:
            import pytz
            from datetime import datetime, timezone as tz
            user_tz = pytz.timezone(user_timezone)
            
            # Конвертируем временные метки в локальное время пользователя
            start_dt = datetime.fromtimestamp(start_of_day, tz=tz.utc).astimezone(user_tz)
            end_dt = datetime.fromtimestamp(end_of_day, tz=tz.utc).astimezone(user_tz)
            
            # Получаем начало и конец дня в UTC
            start_of_day_utc = int(start_dt.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
            end_of_day_utc = int(end_dt.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp())
            
            # Получаем напоминания
            reminders = self.__db.db_read(
                'SELECT row_id, reminder, base_time FROM user_reminders '
                'WHERE user_id = ? AND base_time BETWEEN ? AND ? AND is_active = 1 '
                'ORDER BY base_time',
                (user_id, start_of_day_utc, end_of_day_utc)
            )
            
            # Конвертируем время напоминаний в локальное время пользователя
            formatted_reminders = []
            for reminder in reminders:
                remind_id, remind_text, remind_time = reminder
                remind_dt = datetime.fromtimestamp(remind_time, tz=tz.utc).astimezone(user_tz)
                formatted_reminders.append((remind_id, remind_text, int(remind_dt.timestamp())))
            
            return formatted_reminders
        except Exception as e:
            print(f"Ошибка при обработке часового пояса: {e}")
            # В случае ошибки возвращаем результат без учета часового пояса
            return self.__db.db_read(
                'SELECT row_id, reminder, base_time FROM user_reminders '
                'WHERE user_id = ? AND base_time BETWEEN ? AND ? AND is_active = 1 '
                'ORDER BY base_time',
                (user_id, start_of_day, end_of_day)
            )

    def mark_reminder_as_completed(self, reminder_id: int):
        self.__db.db_write('UPDATE user_reminders SET is_active = False WHERE row_id = ?', (reminder_id,))
        
    def mark_reminder_as_unactive(self, user_id: int, question_id: int):
        self.__db.db_write('UPDATE user_reminders SET is_active = False WHERE user_id = ? AND row_id = ?', (user_id, question_id,))

    def get_user_remind_by_userid(self, user_id: int):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_read('SELECT row_id, reminder, base_time FROM user_reminders WHERE user_id = ? AND is_active = True', (user_id,))
    
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
            data = {'Вопрос': [], 'Ответ': [], 'Последняя запись': []}
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

    def set_user_timezone(self, user_id: int, timezone: str):
        if not self.user_is_existed(user_id):
            return None
        return self.__db.db_write(
            'UPDATE users SET timezone = ? WHERE user_id = ?',
            (timezone, user_id)
        )

    def get_user_timezone(self, user_id: int):
        if not self.user_is_existed(user_id):
            return 'UTC'
        result = self.__db.db_read('SELECT timezone FROM users WHERE user_id = ?', (user_id,))
        return result[0][0] if result else 'UTC'
