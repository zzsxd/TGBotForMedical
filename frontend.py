from telebot import types


class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=1)

    def start_buttons(self):
        one = types.InlineKeyboardButton('🔹 Добавить 10 вопросов', callback_data='add_questions')
        two = types.InlineKeyboardButton('🔹 Настройки давления', callback_data='settings_pressure')
        three = types.InlineKeyboardButton('🔹 Установить часовой пояс', callback_data='timezone_settings')
        self.__markup.add(one, two, three)
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
        four = types.InlineKeyboardButton("Добавить ➕", callback_data="add_reminder")
        five = types.InlineKeyboardButton("Удалить 🗑", callback_data="delete_reminder")
        six = types.InlineKeyboardButton("Часовой пояс 🕥", callback_data="timezone_settings")

        self.__markup.add(one, two, four, five, six)
        return self.__markup
    
    def timezone_buttons(self):
        one = types.InlineKeyboardButton("Петропавловск-Камчатский (+12:00)", callback_data="timezone_petropavlovsk")
        two = types.InlineKeyboardButton('Магадан (+11:00)', callback_data="timezone_magadan")
        three = types.InlineKeyboardButton('Владивосток (+10:00)', callback_data="timezone_vladivostok")
        four = types.InlineKeyboardButton('Якутск (+09:00)', callback_data="timezone_yakutsk")
        five = types.InlineKeyboardButton('Иркутск (+08:00)', callback_data="timezone_irkutsk")
        six = types.InlineKeyboardButton('Новосибирск (+07:00)', callback_data="timezone_irkutsk")
        seven = types.InlineKeyboardButton('Самара (+04:00)', callback_data="timezone_samara")
        eight = types.InlineKeyboardButton('Москва (+03:00)', callback_data="timezone_moscow")
        nine = types.InlineKeyboardButton('Калининград (+02:00)', callback_data="timezone_kaliningrad")
        
        self.__markup.add(one, two, three, four, five, six, seven, eight, nine)
        return self.__markup
        
    
    def repeat_reminder_buttons(self):
        one = types.InlineKeyboardButton("📅 Не повторять", callback_data="no_repeat")
        two = types.InlineKeyboardButton("📅 Ежедневно", callback_data="daily")
        three = types.InlineKeyboardButton("📅 Еженедельно", callback_data="weekly")
        four = types.InlineKeyboardButton("📅 Ежемесячно", callback_data="monthly")
        five = types.InlineKeyboardButton("📅 Выбрать свои дни ", callback_data="custom")

        self.__markup.add(one, two, three, four, five)
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

    def admin_buttons(self):
        one = types.InlineKeyboardButton('📨 Экспортировать пользователей 📨', callback_data='export_users')
        
        self.__markup.add(one)
        return self.__markup
    