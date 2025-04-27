import telebot
import os
import re
import json
import platform
from datetime import datetime
from threading import Lock
from config_parser import ConfigParser
from frontend import Bot_inline_btns
from backend import DbAct
from db import DB

config_name = 'secrets.json'

def main():
    @bot.message_handler(commands=['start', 'admin'])
    def start(message):
        command = message.text.replace('/', '')
        user_id = message.from_user.id
        buttons = Bot_inline_btns()
        db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                            f'@{message.from_user.username}')
        
        if command == 'start':
            if not db_actions.user_is_existed(user_id):
                bot.send_message(user_id, '<b>💙Привет! Я твой персональный помощник!</b>\n\n'
                'С помощью меня, ты можешь:\n'
                '✔ Ежедневно отслеживать давление и вес\n'
                '✔ Записывать напоминания\n'
                '✔ Задавать себе важные вопросы и анализировать ответы\n\n'
                '😊 Давай начнем настройку?',
                parse_mode='HTML', reply_markup=buttons.start_buttons())
            else:
                bot.send_message(user_id, f'<b>👋 Привет, {message.from_user.first_name}! Рад видеть тебя!</b>\n\n'
                '🤓 Выбирай нужный пункт снизу и давай приступим к работе!\n\n',
                parse_mode='HTML', reply_markup=buttons.start_register_buttons())
            

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        user_id = call.message.chat.id
        buttons = Bot_inline_btns()
        if db_actions.user_is_existed(user_id):

            ######## USER ########
            ######## USER NO REG START ########
            if call.data == 'add_questions':
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "🔹 Что это?\n"
                "Это <b>персональные вопросы</b> для ежедневного самоанализа.\n\n"
                "🔹 Зачем это нужно?\n"
                "✔ Психологическая разгрузка", parse_mode='HTML')
                bot.send_message(user_id, "Задайте вопрос №1")
                db_actions.set_user_system_key(user_id, "index", 1)
            elif call.data == "settings_pressure":
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "<b>⚙️ Настройка давления:</b>\n\n"
                "📌 Укажите ваши границы нормы\n" \
                "Введите максимально допустимые значения давления в формате:\n" \
                "❕ Пример: 140/90", parse_mode='HTML')
                db_actions.set_user_system_key(user_id, "index", 13)


            elif call.data == 'end_questions':
                db_actions.set_user_system_key(user_id, "index", None)
                # add to db datas about questions
                questions = db_actions.get_user_question(user_id)
                count = len(questions) if questions else 0
                bot.send_message(user_id, f"❗️ Вы добавили {count} вопроса(ов)", reply_markup=buttons.end_question_two_buttons())
            
            ######## USER IS REG START ########
            elif call.data == 'morning':
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "<b>🌅 Доброе утро!</b> \n\n"
                f"😇 {datetime.today().day} число - отличный день, чтобы позаботиться о себе.", parse_mode='HTML', reply_markup=buttons.morning_buttons())
            
            elif call.data == 'evening':
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "<b>🌇 Добрый вечер!</b> \n\n"
                "🤗 Давай подведем итоги дня и подготовимся к завтра!", parse_mode='HTML', reply_markup=buttons.evening_buttons())
            
            elif call.data == 'pressure':
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "<b>📊 Введите ваше давление</b>\n\n"
                "🤓 Пожалуйста, отправьте ваши текущие показатели в формате:\n"
                "Пример: 120/80", parse_mode="HTML")
                db_actions.set_user_system_key(user_id, "index", 15)
            
            elif call.data == 'reports':
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "<b>📊 Отчеты:</b>\n\n" \
                "🧐 Выберите нужный пункт и получите сведения!", parse_mode="HTML", reply_markup=buttons.reports_buttons())
            
            elif call.data == 'reminders':
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "<b>Напоминания:</b>\n\n" \
                "📄 Выберите, за какой период получить напоминания?", parse_mode="HTML", reply_markup=buttons.reminders_buttons())

            elif call.data == 'settings':
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "<b>⚙️ Настройки:</b>\n\n" \
                "📌 Здесь вы можете!\n" \
                "✔ Добавить/Удалить вопросы\n" \
                "✔ Настроить давление\n" \
                "✔ Настроить таблетки", parse_mode="HTML", reply_markup=buttons.settings_buttons())

            ######## MORNING BUTTONS ########
            elif call.data == 'reminders_today':
                # bot send message with today reminders
                db_actions.set_user_system_key(user_id, "index", None)
            elif call.data == 'pressure_today':
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "<b>📌 Отправьте ваше давление сейчас</b>\n\n" \
                "❕ Пример: 140/90", parse_mode='HTML')
                db_actions.set_user_system_key(user_id, "index", 15)
            elif call.data == 'weight_today':
                # bot send message with request to add data about weight
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "<b>💪 Отправьте ваш вес</b>\n\n" \
                "❕ Пример: 75", parse_mode='HTML')
                db_actions.set_user_system_key(user_id, "index", 12)
        
            ######## EVENING BUTTONS ########
            elif call.data == 'plans_tomorrow':
                # bot send message with request to add data about plans at tomorrow
                db_actions.set_user_system_key(user_id, "index", None)
            elif call.data == 'answer_on_questions':
                # bot send questions, user need answer
                db_actions.set_user_system_key(user_id, "index", None)
                question = db_actions.get_user_question(user_id)[0][1]
                bot.send_message(user_id, "<b>📌 Ответить на вопросы:</b>\n\n" \
                f"{question}", parse_mode='HTML')
                # db_actions.set_user_system_key(user_id, "index", ??)
            
            ######## REPORTS BUTTONS ########
            elif call.data == "pressure_report":
                # bot send xlsx with pressure?
                db_actions.set_user_system_key(user_id, "index", None)
            elif call.data == "weight_report":
                #bot send xlsx with weight?
                db_actions.set_user_system_key(user_id, "index", None)
            elif call.data == "questions_report":
                # bot send xlsx with q/a?
                db_actions.set_user_system_key(user_id, "index", None)

            ######## REMINDERS BUTTONS ########
            elif call.data == "reminders_today":
                # bot send reminders at today
                db_actions.set_user_system_key(user_id, "index", None)
            elif call.data == "all_reminders":
                # bot send all reminders
                db_actions.set_user_system_key(user_id, "index", None)
            elif call.data == "add_reminder":
                # user add remind
                db_actions.set_user_system_key(user_id, "index", None)
            elif call.data == "delete_reminder":
                # user delete remind
                db_actions.set_user_system_key(user_id, "index", None)
            elif call.data == "reminder_settings":
                # ???
                db_actions.set_user_system_key(user_id, "index", None)

            ######## SETTINGS BUTTONS ########
            elif call.data == "two_add_questions":
                db_actions.set_user_system_key(user_id, "index", None)
                # user add questions
            elif call.data == "delete_questions":
                db_actions.set_user_system_key(user_id, "index", None)
                questions = db_actions.get_user_question(user_id)
                if not questions:
                    bot.send_message(user_id, '❌ У вас нет вопросов!\n\n'
                    '📌 Нажмите на кнопку ниже, чтобы добавить их', reply_markup=buttons.add_question_btns())
                questions_list = []
                for idx, (q_id, q_text) in enumerate(questions, start=1):
                    questions_list.append(f"{idx}. {q_text}")
                questions_text = "\n".join(questions_list)
                bot.send_message(
                    user_id,
                    f"Введите номер вопроса для удаления:\n\n{questions_text}")
                db_actions.set_user_system_key(user_id, "index", 11)
            elif call.data == "pressure_settings":
                # pressure settings
                db_actions.set_user_system_key(user_id, "index", None)
                pressure_settings = db_actions.get_user_pressure_setting(user_id)[0][0]
                pills_settings = db_actions.get_user_pressure_setting(user_id)[0][1]
                bot.send_message(user_id, "<b>⚙️ Настройки давления:</b>\n\n" \
                "Ваши текущие параметры:\n" \
                f"📊 Максимальный порог давления: {pressure_settings}\n"
                f"💊 Таблетки: {pills_settings}", parse_mode='HTML', reply_markup=buttons.pressure_settings())
            elif call.data == 'set_pressure':
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "<b>📌 Укажите ваши максимально допустимые границы давления в формате:</b>\n" \
                "❕ Пример: 140/90", parse_mode='HTML')
                db_actions.set_user_system_key(user_id, "index", 16)
            elif call.data == 'set_pills':
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, '<b>📌 Укажите таблетки, которые следует принимать при высоком давлении!<b>')
                db_actions.set_user_system_key(user_id, "index", 17)




    @bot.message_handler(content_types=['text', 'photo'])
    def text_message(message):
        user_input = message.text
        user_id = message.chat.id
        buttons = Bot_inline_btns()
        code = db_actions.get_user_system_key(user_id, "index")
        if db_actions.user_is_existed(user_id):
            if db_actions.user_is_admin(user_id):
                # 0-10 codes for user questions
                if code != 11 and code in range(1, 11):
                    db_actions.write_user_question(user_id, code, user_input)
                    code += 1
                    db_actions.set_user_system_key(user_id, "index", code)
                    bot.send_message(user_id, f"Задайте вопрос №{code}", reply_markup=buttons.end_question_buttons())
                elif code == 11:
                    # code for delete question
                    # user_input = question_id
                    db_actions.delete_user_question(user_input, user_id)
                    bot.send_message(user_id, '✅ Вопрос удален!')
                elif code == 12:
                    # code for add data about user max weight
                    db_actions.add_user_weight(user_id, user_input)
                    bot.send_message(user_id, "✅ Данные добавлены!", reply_markup=buttons.reports_buttons())
                elif code == 13:
                    # 13 and 14 codes for user pressure settings
                    db_actions.set_user_system_key(user_id, "pressure", user_input)
                    bot.send_message(user_id, "<b>✅ Данные о максимальном давлении внесены!</b>\n\n" \
                    "📌 Какие таблетки следует принимать при таком давлении?", parse_mode='HTML')
                    db_actions.set_user_system_key(user_id, "index", 14)
                elif code == 14:
                    pressure = db_actions.get_user_system_key(user_id, "pressure")
                    db_actions.add_user_settings(user_id, pressure, user_input)
                    bot.send_message(user_id, "<b>✅ Данные о таблетках записаны!</b>", parse_mode='HTML')
                elif code == 15:
                    # code for user input pressure today
                    db_actions.add_pressure_user(user_id, user_input)
                    bot.send_message(user_id, "<b>✅ Данные успешно записаны</b>\n\n"
                    f"Ваше давление: {user_input}", parse_mode='HTML')
                    pressure_settings = db_actions.get_user_pressure_setting(user_id)[0][0]
                    pills_settings = db_actions.get_user_pressure_setting(user_id)[0][1]
                    if pressure_settings and pills_settings:
                        max_systolic, max_diastolic = map(int, pressure_settings.split('/'))
                        now_systolic, now_diastolic = map(int, user_input.split('/'))
                        if now_systolic >= max_systolic or now_diastolic >= max_diastolic:
                            bot.send_message(user_id, "<b>⚠️ Давление выше порогового значения!</b>\n\n" \
                            f"💊 Следует приянять: {pills_settings}", parse_mode='HTML')
                        else:
                            bot.send_message(user_id, '<b>📊 Ваше давление соответствует нормальным показателям!</b>\nОтличный результат! ✅', parse_mode='HTML')
                    else:
                        bot.send_message(user_id, "❌ Ошибка!\n\nНет данных о пороге давления или таблетках!", reply_markup=buttons.end_question_two_buttons())
                elif code == 16:
                    db_actions.update_user_pressure_setting(user_id, user_input)
                    bot.send_message(user_id, "<b>✅ Данные обновлены!</b>", parse_mode='HTML')
                elif code == 17:
                    db_actions.update_user_pills_setting(user_id, user_input)
                    bot.send_message(user_id, "<b>✅ Данные обновлены!</b>", parse_mode='HTML')
                

    
    
    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(f'{work_dir}/{config_name}', os_type)
    db = DB(config.get_config()['db_file_name'], Lock())
    db_actions = DbAct(db, config)
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()