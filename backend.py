import json


class DbAct:
    def __init__(self, db, config):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config

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
                                                                        "remind": None}), is_admin))
            

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

    def add_user_weight(self, user_id: int, weight: int):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO user_datas (user_id, weight) VALUES (?, ?)', (user_id, weight))

    def add_user_settings(self, user_id: int, pressure: str, pills: str):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO user_settings (user_id, pressure, pills) VALUES (?, ?, ?)', (user_id, pressure, pills))

    def add_pressure_user(self, user_id: int, pressure: str):
        if not self.user_is_existed(user_id):
            return None
        self.__db.db_write('INSERT INTO user_datas (user_id, pressure) VALUES (?, ?)', (user_id, pressure))

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
        self.__db.db_write('INSERT INTO user_reminders (user_id, reminder, time) VALUES (?, ?, ?)', (user_id, remind, time))