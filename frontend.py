from telebot import types


class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=1)

    def start_buttons(self):
        one = types.InlineKeyboardButton('🔹 Добавить 10 вопросов', callback_data='add_questions')
        two = types.InlineKeyboardButton('🔹 Настройки давления', callback_data='settings_pressure')
        self.__markup.add(one, two)
        return self.__markup
    
    def end_question_buttons(self):
        one = types.InlineKeyboardButton("✅ Закончить", callback_data="end_questions")

        self.__markup.add(one)
        return self.__markup
    
    def start_register_buttons(self):
        one = types.InlineKeyboardButton("Утро 🌅", callback_data="morning")
        two = types.InlineKeyboardButton("Вечер 🌃", callback_data="evening")
        three = types.InlineKeyboardButton("Давление 💊", callback_data="pressure")
        four = types.InlineKeyboardButton("Отчеты 📊", callback_data="reports")
        five = types.InlineKeyboardButton("Напоминания 📅", callback_data="reminders")
        six = types.InlineKeyboardButton("Настройки ⚙️", callback_data="settings")

        self.__markup.add(one, two, three, four, five, six)
        return self.__markup
    
    def morning_buttons(self):
        one = types.InlineKeyboardButton("📅 Напоминания", callback_data="reminders_today")
        two = types.InlineKeyboardButton("💊 Давление", callback_data="pressure_today")
        three = types.InlineKeyboardButton("💪 Вес", callback_data="weight_today")

        self.__markup.add(one, two, three)
        return self.__markup
    
    def evening_buttons(self):
        one = types.InlineKeyboardButton("📅 Планы", callback_data="plans_tomorrow")
        two = types.InlineKeyboardButton("💊 Давление", callback_data="pressure_today")
        three = types.InlineKeyboardButton("📄 Ответить на вопросы", callback_data="answer_on_questions")
        
        self.__markup.add(one, two, three)
        return self.__markup
    
    def reports_buttons(self):
        one = types.InlineKeyboardButton("Отчет по давлению 💊", callback_data="pressure_report")
        two = types.InlineKeyboardButton("Отчет по весу 💪", callback_data="weight_report")
        three = types.InlineKeyboardButton("Отчет по вопросам 📄", callback_data="questions_report")

        self.__markup.add(one, two, three)
        return self.__markup
    
    def reminders_buttons(self):
        one = types.InlineKeyboardButton("За сегодня 📅", callback_data="reminders_today")
        two = types.InlineKeyboardButton("Все напоминания 📄", callback_data="all_reminders")
        three = types.InlineKeyboardButton("Настроить ⚙️", callback_data="reminder_settings")
        four = types.InlineKeyboardButton("Добавить ➕", callback_data="add_reminder")
        five = types.InlineKeyboardButton("Удалить 🗑", callback_data="delete_reminder")

        self.__markup.add(one, two, four, five, three)
        return self.__markup
    
    def settings_buttons(self):
        one = types.InlineKeyboardButton("➕ Добавить вопросы", callback_data="two_add_questions")
        two = types.InlineKeyboardButton("🗑 Удалить вопросы", callback_data="delete_questions")
        three = types.InlineKeyboardButton("💊 Давление", callback_data="pressure_settings")

        self.__markup.add(one, two, three)
        return self.__markup
    
    def add_question_btns(self):
        one = types.InlineKeyboardButton("➕ Добавить вопросы", callback_data='two_add_questions')

        self.__markup.add(one)
        return self.__markup
    
    def end_question_two_buttons(self):
        one = types.InlineKeyboardButton("🔹 Настройки давления", callback_data='settings_pressure')

        self.__markup.add(one)
        return self.__markup

    def pressure_settings(self):
        one = types.InlineKeyboardButton("⚙️ Настроить давление", callback_data="set_pressure")
        two = types.InlineKeyboardButton("⚙️ Настроить таблетки", callback_data="set_pills")

        self.__markup.add(one, two)
        return self.__markup
