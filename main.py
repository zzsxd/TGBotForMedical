import time
import telebot
import os
import re
import json
import threading
import platform
from datetime import datetime
from threading import Lock
from config_parser import ConfigParser
from frontend import Bot_inline_btns
from telebot import types
from backend import DbAct
from db import DB

config_name = 'secrets.json'

# Глобальная переменная для хранения потока
reminder_thread = None

def main():
    @bot.message_handler(commands=['start', 'admin'])
    def start(message):
        command = message.text.replace('/', '')
        user_id = message.from_user.id
        buttons = Bot_inline_btns()
        if command == 'start':
            db_actions.set_user_system_key(user_id, "index", None)
            if db_actions.user_is_existed(user_id) == False:
                db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                            f'@{message.from_user.username}')
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
        elif command == 'admin':
            bot.send_message(user_id, "<b>Добро пожаловать в Админ-Панель!</b>"
                             "\n\nВыберите пункт ниже!", reply_markup=buttons.admin_buttons(), parse_mode='HTML')
            

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        user_id = call.message.chat.id
        buttons = Bot_inline_btns()
        if db_actions.user_is_existed(user_id):
            if db_actions.user_is_admin(user_id):
                if call.data == 'export_users':
                    db_actions.db_export_xlsx()
                    bot.send_document(user_id, open(config.get_config()['xlsx_path'], 'rb'))
                    os.remove(config.get_config()['xlsx_path'])

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
                # ad to db datas about questions
                questions = db_actions.get_user_question(user_id)
                count = len(questions) if questions else 0
                bot.send_message(user_id, f"❗️ Всего: {count} вопроса(ов)", reply_markup=buttons.end_question_two_buttons())
            
            ######## USER IS REG START ########
            
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

            elif call.data == 'timezone_settings':
                db_actions.set_user_system_key(user_id, "index", None)
                current_timezone = db_actions.get_user_timezone(user_id)
                bot.send_message(
                    user_id,
                    f"⏰ Текущий часовой пояс: {current_timezone}\n\n"
                    "Выберите ваш город для установки часового пояса:",
                    parse_mode="HTML",
                    reply_markup=buttons.timezone_buttons()
                )

            elif call.data.startswith('timezone_'):
                timezone_map = {
                    'timezone_petropavlovsk': 'Asia/Kamchatka',
                    'timezone_magadan': 'Asia/Magadan',
                    'timezone_vladivostok': 'Asia/Vladivostok',
                    'timezone_yakutsk': 'Asia/Yakutsk',
                    'timezone_irkutsk': 'Asia/Irkutsk',
                    'timezone_novosibirsk': 'Asia/Novosibirsk',
                    'timezone_samara': 'Europe/Samara',
                    'timezone_moscow': 'Europe/Moscow',
                    'timezone_kaliningrad': 'Europe/Kaliningrad'
                }
                
                timezone = timezone_map.get(call.data)
                if timezone:
                    if db_actions.set_user_timezone(user_id, timezone):
                        bot.answer_callback_query(call.id, f"✅ Часовой пояс установлен: {timezone}")
                        bot.edit_message_text(
                            f"⏰ Ваш часовой пояс установлен: {timezone}",
                            call.message.chat.id,
                            call.message.message_id
                        )
                    else:
                        bot.answer_callback_query(call.id, "❌ Ошибка при установке часового пояса")

            elif call.data == 'settings':
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "<b>⚙️ Настройки:</b>\n\n" \
                "📌 Здесь вы можете!\n" \
                "✔ Добавить/Удалить вопросы\n" \
                "✔ Настроить давление\n" \
                "✔ Настроить таблетки\n" \
                "✔ Настроить часовой пояс", parse_mode="HTML", reply_markup=buttons.settings_buttons())

            ######## MORNING BUTTONS ########

                    
            # elif call.data == 'weight_today':
            #     # bot send message with request to add data about weight
            #     db_actions.set_user_system_key(user_id, "index", None)
            #     bot.send_message(user_id, "<b>💪 Отправьте ваш вес</b>\n\n" \
            #     "❕ Пример: 75", parse_mode='HTML')
            #     db_actions.set_user_system_key(user_id, "index", 12)
        
            ######## EVENING BUTTONS ########
            elif call.data == 'plans_tomorrow':
                # bot send message with request to add data about plans at tomorrow
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "<b>Давайте составим план на завтра!</b>\n\n" \
                "Напишите, о чем мне напомнить завтра?\n" \
                "(в формате одного сообщения)", parse_mode='HTML')
                db_actions.set_user_system_key(user_id, "index", 18)

            elif call.data == 'answer_on_questions':
                # bot send questions, user need answer
                db_actions.set_user_system_key(user_id, "index", None)
                questions = db_actions.get_user_question(user_id)
                
                if not questions:
                    bot.send_message(user_id, "❌ У вас нет вопросов")
                    return
                db_actions.set_user_system_key(user_id, "pending_questions", 
                                            [q[0] for q in questions])  # Сохраняем IDs вопросов
                db_actions.set_user_system_key(user_id, "current_question_index", 0)
                first_question = questions[0][1]  # questions[0][1] - текст вопроса
                bot.send_message(
                    user_id,
                    "<b>📌 Ответьте на вопросы:</b>\n\n"
                    f"1/{len(questions)}. {first_question}\n\n"
                    "Введите ваш ответ:",
                    parse_mode='HTML'
                )
                db_actions.set_user_system_key(user_id, "index", 21)
            
            ######## REPORTS BUTTONS ########
            elif call.data == "pressure_report":
                # bot send xlsx with pressure
                db_actions.set_user_system_key(user_id, "index", None)
                try:
                    db_actions.get_pressure_report(user_id)
                    bot.send_document(user_id, open(config.get_config()['xlsx_path'], 'rb'))
                    os.remove(config.get_config()['xlsx_path'])
                except Exception:
                    bot.send_message(user_id, "❌ Нет данных!")
            elif call.data == "weight_report":
                #bot send xlsx with weight
                db_actions.set_user_system_key(user_id, "index", None)
                try:
                    db_actions.get_weight_report(user_id)
                    bot.send_document(user_id, open(config.get_config()['xlsx_path'], 'rb'))
                    os.remove(config.get_config()['xlsx_path'])
                except Exception:
                    bot.send_message(user_id, "❌ Нет данных!")
            elif call.data == "questions_report":
                # bot send xlsx with q/a
                db_actions.set_user_system_key(user_id, "index", None)
                try:
                    db_actions.get_question_answer_report(user_id)
                    bot.send_document(user_id, open(config.get_config()['xlsx_path'], 'rb'))
                    os.remove(config.get_config()['xlsx_path'])
                except Exception:
                    bot.send_message(user_id, "❌ Нет данных!")

            ######## REMINDERS BUTTONS ########
            elif call.data == 'all_reminders':
                from datetime import datetime
                
                try:
                    db_actions.set_user_system_key(user_id, "index", None)
                    reminds = db_actions.get_user_remind_by_userid(user_id)
                    
                    if not reminds:
                        bot.send_message(user_id, "❌ У вас нет активных напоминаний")
                        return
                    
                    reminds_list = []
                    for idx, remind in enumerate(reminds, start=1):
                        remind_id = remind[0]  # row_id
                        remind_text = remind[1]  # текст напоминания
                        remind_timestamp = remind[2]  # метка времени
                        repeat_type = remind[3]  # тип повторения
                        custom_days = remind[4]  # кастомные дни (если есть)
                        
                        # Преобразуем timestamp в читаемый формат
                        remind_time = datetime.fromtimestamp(remind_timestamp)
                        formatted_time = remind_time.strftime('%d.%m.%Y %H:%M')
                        
                        # Формируем строку с типом повторения
                        repeat_info = ""
                        if repeat_type == 'no_repeat':
                            repeat_info = "без повторения"
                        elif repeat_type == 'daily':
                            repeat_info = "ежедневно"
                        elif repeat_type == 'weekly':
                            repeat_info = "еженедельно"
                        elif repeat_type == 'monthly':
                            repeat_info = "ежемесячно"
                        elif repeat_type == 'custom' and custom_days:
                            days_map = {
                                '1': 'понедельник',
                                '2': 'вторник',
                                '3': 'среда',
                                '4': 'четверг',
                                '5': 'пятница',
                                '6': 'суббота',
                                '7': 'воскресенье'
                            }
                            # Сортируем дни по порядку (1-7) перед отображением
                            sorted_days = sorted(custom_days.split(','), key=int)
                            days_names = [days_map[d] for d in sorted_days]
                            repeat_info = f"каждый {', '.join(days_names)}"
                        
                        reminds_list.append(f"{idx}. {remind_text} - {formatted_time}, {repeat_info}")
                    
                    # Отправляем пользователю список
                    bot.send_message(
                        user_id,
                        "📄 Ваши активные напоминания:\n\n" + "\n".join(reminds_list),
                        parse_mode="HTML"
                    )
                
                except Exception as e:
                    print(f"Error in all_reminders: {e}")
                    bot.send_message(user_id, "❌ Произошла ошибка при получении напоминаний")

            elif call.data == "add_reminder":
                # user add remind
                db_actions.set_user_system_key(user_id, "index", None)
                bot.send_message(user_id, "<b>Давайте составим план на завтра!</b>\n\n" \
                "Напишите, о чем мне напомнить завтра?\n" \
                "(в формате одного сообщения)", parse_mode='HTML')
                db_actions.set_user_system_key(user_id, "index", 18)

            elif call.data == "delete_reminder":
                from datetime import datetime
                # user delete remind
                db_actions.set_user_system_key(user_id, "index", None)
                reminds = db_actions.get_user_remind_by_userid(user_id)
                
                if not reminds:
                    bot.send_message(user_id, "❌ У вас нет активных напоминаний")
                    return
                
                # Формируем список напоминаний с нумерацией
                reminds_list = []
                for idx, remind in enumerate(reminds, start=1):
                    remind_id = remind[0]  # ID напоминания
                    remind_text = remind[1]  # Текст напоминания
                    remind_timestamp = remind[2]  # Время в timestamp
                    
                    # Форматируем время
                    remind_time = datetime.fromtimestamp(remind_timestamp)
                    formatted_time = remind_time.strftime('%d.%m.%Y %H:%M')
                    
                    reminds_list.append(
                        f"{idx}. {remind_text} - {formatted_time} [ID: {remind_id}]"
                    )
                
                # Отправляем список пользователю
                bot.send_message(
                    user_id,
                    "📄 Ваши активные напоминания:\n\n" +
                    "\n".join(reminds_list) +
                    "\n\nДля удаления отправьте <b>ID</b> напоминания\n" +
                    "Или введите 0 для отмены",
                    parse_mode="HTML"
                )
                db_actions.set_user_system_key(user_id, "index", 20)


            elif call.data in ['no_repeat', 'daily', 'weekly', 'monthly', 'custom']:
                remind_text = db_actions.get_user_system_key(user_id, "remind")
                time_remind = db_actions.get_user_system_key(user_id, "time_remind")
                if not remind_text:
                    bot.send_message(user_id, "❌ Текст напоминания не найден")
                    return
                
                if call.data == 'custom':
                    bot.send_message(
                        user_id,
                        "Введите дни недели через запятую (1-Пн, 2-Вт, ..., 7-Вс):",
                        reply_markup=types.ForceReply()
                    )
                    db_actions.set_user_system_key(user_id, "index", 23)
                else:
                    # Получаем часовой пояс пользователя
                    user_timezone = db_actions.get_user_timezone(user_id)
                    if not user_timezone:
                        user_timezone = 'UTC'
                    
                    try:
                        import pytz
                        from datetime import datetime, timezone as tz, timedelta
                        user_tz = pytz.timezone(user_timezone)
                        
                        # Конвертируем время напоминания в локальное время пользователя
                        remind_dt = datetime.fromtimestamp(time_remind, tz=tz.utc).astimezone(user_tz)
                        
                        # Вычисляем next_time в зависимости от типа повторения
                        if call.data == 'daily':
                            next_time = remind_dt + timedelta(days=1)
                        elif call.data == 'weekly':
                            next_time = remind_dt + timedelta(weeks=1)
                        elif call.data == 'monthly':
                            next_time = remind_dt + timedelta(days=30)
                        else:  # no_repeat
                            next_time = remind_dt
                        
                        # Конвертируем обратно в UTC для хранения
                        next_time_utc = int(next_time.astimezone(tz.utc).timestamp())
                        
                        if db_actions.add_reminder(user_id, remind_text, time_remind, call.data):
                            bot.send_message(user_id, "✅ Напоминание установлено!")
                        else:
                            bot.send_message(user_id, "❌ Ошибка при создании напоминания")
                    except Exception as e:
                        print(f"Ошибка при установке повторяющегося напоминания: {e}")
                        bot.send_message(user_id, "❌ Ошибка при создании напоминания")
                    
                    db_actions.set_user_system_key(user_id, "index", None)




            ######## SETTINGS BUTTONS ########
            elif call.data == "two_add_questions":
                db_actions.set_user_system_key(user_id, "index", None)
                questions = db_actions.get_user_question(user_id)
                count = len(questions) if questions else 0
                if count >= 10:
                    bot.send_message(user_id, "<b>❌ У вас добавлено максимальное количество вопросов!</b>", parse_mode='HTML')
                else:
                    bot.send_message(user_id, "📌 Задайте вопрос")
                    db_actions.set_user_system_key(user_id, "index", 1)
            elif call.data == "delete_questions":
                db_actions.set_user_system_key(user_id, "index", None)
                questions = db_actions.get_user_question(user_id)
                if not questions:
                    bot.send_message(user_id, '❌ У вас нет вопросов!\n\n'
                    '📌 Нажмите на кнопку ниже, чтобы добавить их', reply_markup=buttons.add_question_btns())
                    return
                questions_list = []
                for idx, (q_id, q_text, *_) in enumerate(questions, start=1):
                    questions_list.append(f"{idx}. {q_text} [ID: {q_id}]")
                questions_text = "\n".join(questions_list)
                bot.send_message(
                    user_id,
                    "📋 Список ваших вопросов:\n\n" +
                    "\n".join(questions_list) +
                    "\n\nВведите <b>ID вопроса</b> для удаления:",
                    parse_mode='HTML'
                )
                db_actions.set_user_system_key(user_id, "index", 11)
            elif call.data == "edit_question":
                db_actions.set_user_system_key(user_id, "index", None)
                questions = db_actions.get_user_question(user_id)
                if not questions:
                    bot.send_message(user_id, '❌ У вас нет вопросов!\n\n'
                    '📌 Нажмите на кнопку ниже, чтобы добавить их', reply_markup=buttons.add_question_btns())
                    return
                questions_list = []
                for idx, (q_id, q_text, *_) in enumerate(questions, start=1):
                    questions_list.append(f"{idx}. {q_text} [ID: {q_id}]")
                questions_text = "\n".join(questions_list)
                bot.send_message(
                    user_id,
                    "📋 Список ваших вопросов:\n\n" +
                    "\n".join(questions_list) +
                    "\n\nВведите <b>ID вопроса</b> для редактирования:",
                    parse_mode='HTML'
                )
                db_actions.set_user_system_key(user_id, "index", 24)
            elif call.data == "pressure_settings":
                # pressure settings
                db_actions.set_user_system_key(user_id, "index", None)
                if not db_actions.get_user_pressure_setting(user_id):
                    bot.send_message(user_id, "❌ Нет данных о давлении или таблетках!", reply_markup=buttons.pressure_settings())
                    db_actions.set_user_system_key(user_id, "index", None)
                    return  
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
                bot.send_message(user_id, '<b>📌 Укажите таблетки, которые следует принимать при высоком давлении!</b>\n\n', parse_mode='HTML')
                db_actions.set_user_system_key(user_id, "index", 17)

            elif call.data == "question_settings":
                bot.send_message(user_id, "⚙️ Настройки вопросов\n\n"
                "Выберите пункт ниже!", reply_markup=buttons.question_settings_buttons())

            elif call.data == "reminder_settings":
                bot.send_message(user_id, "⚙️ Настройки напоминаний\n\n"
                "Выберите пункт ниже!", reply_markup=buttons.reminders_buttons())


    @bot.message_handler(content_types=['text'])
    def text_message(message):
        user_input = message.text
        user_id = message.chat.id
        buttons = Bot_inline_btns()
        code = db_actions.get_user_system_key(user_id, "index")
        if db_actions.user_is_existed(user_id):
            # 0-10 codes for user questions
            if code != 11 and code in range(1, 11):
                if len(user_input) > 120:
                    bot.send_message(user_id, "<b>❌ Превышение лимита символов!</b>\n\n"
                    "Максимум: 120 символов", parse_mode='HTML')
                    return
                else:
                    questions = db_actions.get_user_question(user_id)
                    count = len(questions) if questions else 0
                    if count >= 10:
                        bot.send_message(user_id, "<b>❌ У вас добавлено максимальное количество вопросов!</b>", parse_mode='HTML')
                        db_actions.set_user_system_key(user_id, "index", None)
                    else:
                        db_actions.write_user_question(user_id, code, user_input)
                        code += 1
                        db_actions.set_user_system_key(user_id, "index", code)
                        bot.send_message(user_id, f"Задайте вопрос №{code}", reply_markup=buttons.end_question_buttons())
            elif code == 11:
                # code for delete question
                try:
                    if user_input.strip() == "0":
                        bot.send_message(user_id, "✅ Удаление отменено")
                        db_actions.set_user_system_key(user_id, "index", None)
                    question_id = int(user_input.strip())
                    if not question_id:
                        bot.send_message(user_id, "❌ Ошибка! Введите ID вопроса!")
                        return
                    else:
                        check_question = db_actions.question_is_exist(user_id, question_id)
                        if not check_question:
                            bot.send_message(user_id, "❌ Ошибка! Вопрос не найден!")
                            return
                        else:
                            db_actions.delete_user_question(question_id, user_id)
                            bot.send_message(user_id, '✅ Вопрос удален!')
                            db_actions.set_user_system_key(user_id, "index", None)

                except:
                    bot.send_message(user_id, "❌ Ошибка! Введите ID вопроса!")
            elif code == 12:
                # code for add data about user today weight
                if len(user_input) > 3:
                    bot.send_message(user_id, "❌ Ошибка!")
                    db_actions.set_user_system_key(user_id, "index", None)
                    return
                else:
                    try:
                        weight = int(user_input)
                        db_actions.add_user_weight(user_id, weight)
                        bot.send_message(user_id, "✅ Данные добавлены!", reply_markup=buttons.reports_buttons())
                    except:
                        bot.send_message(user_id, "❌ Ошибка!")
                    
            elif code == 13:
                # 13 and 14 codes for user pressure settings
                try:
                    now_systolic, now_diastolic = map(int, user_input.split('/'))
                    if now_systolic and now_diastolic:
                        db_actions.set_user_system_key(user_id, "pressure", user_input)
                        bot.send_message(user_id, "<b>✅ Данные о максимальном давлении внесены!</b>\n\n" \
                        "📌 Какие таблетки следует принимать при таком давлении?", parse_mode='HTML')
                        db_actions.set_user_system_key(user_id, "index", 14)
                    else:
                        bot.send_message(user_id, "❌ Ошибка! Введите давление в формате: 120/60")
                except:
                    bot.send_message(user_id, "❌ Ошибка!")
            elif code == 14:
                if len(user_input) > 120:
                    bot.send_message(user_id, "<b>❌ Превышение лимита символов!</b>\n\n"
                    "Максимум: 120 символов", parse_mode='HTML')
                    return
                else:
                    pressure = db_actions.get_user_system_key(user_id, "pressure")
                    db_actions.add_user_settings(user_id, pressure, user_input)
                    bot.send_message(user_id, "<b>✅ Данные о таблетках записаны!</b>", parse_mode='HTML')
            elif code == 15:
                # code for user input pressure today
                try:
                    now_systolic, now_diastolic = map(int, user_input.split('/'))
                    if now_systolic and now_diastolic:
                        if now_systolic > 180 or now_diastolic > 140 or now_systolic < 50 or now_diastolic < 50:
                            bot.send_message(user_id, '❌ Неверные данные!')
                            return
                        else:
                            bot.send_message(user_id, "<b>✅ Данные успешно записаны</b>\n\n"
                            f"Ваше давление: {user_input}", parse_mode='HTML')
                            if not db_actions.get_user_pressure_setting(user_id):
                                bot.send_message(user_id, "❌ Нет данных о давлении или таблетках!", reply_markup=buttons.pressure_settings())
                                return  
                            pressure_settings = db_actions.get_user_pressure_setting(user_id)[0][0]
                            pills_settings = db_actions.get_user_pressure_setting(user_id)[0][1]
                        if pressure_settings and pills_settings:
                            max_systolic, max_diastolic = map(int, pressure_settings.split('/'))
                            if now_systolic >= max_systolic or now_diastolic >= max_diastolic:
                                bot.send_message(user_id, "<b>⚠️ Давление выше порогового значения!</b>\n\n" \
                                f"💊 Следует приянять: {pills_settings}", parse_mode='HTML')
                                bot.send_message(user_id, "📊 Введите причину такого давления!")
                                db_actions.set_user_system_key(user_id, "now_pressure", user_input)
                                db_actions.set_user_system_key(user_id, "index", 22)
                            else:
                                bot.send_message(user_id, '<b>📊 Ваше давление соответствует нормальным показателям!</b>\nОтличный результат! ✅', parse_mode='HTML')
                                cause = 'Давление в норме'
                                db_actions.add_pressure_user(user_id, user_input, cause)
                        else:
                            bot.send_message(user_id, "❌ Ошибка!\n\nНет данных о пороге давления или таблетках!", reply_markup=buttons.end_question_two_buttons())
                    else:
                        bot.send_message(user_id, "❌ Ошибка! Введите давление в формате: 120/60")
                except:
                    bot.send_message(user_id, "❌ Ошибка!")
            elif code == 16:
                # 16 and 17 codes for user_settings
                try:
                    now_systolic, now_diastolic = map(int, user_input.split('/'))
                    if now_systolic and now_diastolic:
                        if now_systolic > 180 or now_diastolic > 140 or now_systolic < 50 or now_diastolic < 50:
                            bot.send_message(user_id, '❌ Неверные данные!')
                            return
                        else:
                            db_actions.update_user_pressure_setting(user_id, user_input)
                            bot.send_message(user_id, "<b>✅ Данные обновлены!</b>", parse_mode='HTML')
                    else:
                        bot.send_message(user_id, "❌ Ошибка! Введите давление в формате: 120/60")
                except:
                    bot.send_message(user_id, "❌ Ошибка!")
            elif code == 17:
                if len(user_input) > 120:
                    bot.send_message(user_id, "<b>❌ Превышение лимита символов!</b>\n\n"
                    "Максимум: 120 символов", parse_mode='HTML')
                    return
                else:
                    db_actions.update_user_pills_setting(user_id, user_input)
                    bot.send_message(user_id, "<b>✅ Данные обновлены!</b>", parse_mode='HTML')
                    db_actions.set_user_system_key(user_id, "index", None)

            elif code == 18:
                # 18 and 19 codes for user reminders at tommorow
                if len(user_input) > 120:
                    bot.send_message(user_id, "<b>❌ Превышение лимита символов!</b>\n\n"
                    "Максимум: 120 символов", parse_mode='HTML')
                    return
                else:
                    db_actions.set_user_system_key(user_id, "remind", user_input)
                    bot.send_message(user_id, "<b>⏰ В какое время вам напомнить об этом?</b>\n" \
                    "Пример: <b>25.12.2025 18:00</b>", parse_mode='HTML')
                    db_actions.set_user_system_key(user_id, "index", 19)
            elif code == 19:
                remind = db_actions.get_user_system_key(user_id, "remind")
                try:
                    # Получаем часовой пояс пользователя
                    user_timezone = db_actions.get_user_timezone(user_id)
                    if not user_timezone:
                        user_timezone = 'UTC'
                    
                    import pytz
                    from datetime import datetime, timezone as tz
                    user_tz = pytz.timezone(user_timezone)
                    
                    # Парсим введенную дату в локальном времени пользователя
                    time_dt = datetime.strptime(user_input, '%d.%m.%Y %H:%M')
                    time_dt = user_tz.localize(time_dt)
                    
                    # Получаем текущее время в часовом поясе пользователя
                    current_time = datetime.now(user_tz)
                    
                    if time_dt < current_time:
                        bot.send_message(user_id, "❌ Ошибка!\n" \
                        "Введенная дата в прошлом!\n\n" \
                        "Введите дату еще раз, пример: <b>25.12.2025 18:00</b>", parse_mode='HTML')
                        db_actions.set_user_system_key(user_id, "index", 19)
                        return
                    else:
                        # Конвертируем время в UTC для хранения
                        timestamp = int(time_dt.astimezone(tz.utc).timestamp())
                        db_actions.set_user_system_key(user_id, "time_remind", timestamp)
                        bot.send_message(user_id, "✅ Напоминание установлено!")
                        bot.send_message(user_id, "⏰ Выберите повтор напоминания", reply_markup=buttons.repeat_reminder_buttons())
                        db_actions.set_user_system_key(user_id, "index", None)
                except ValueError:
                    bot.send_message(user_id, "❌ Неверный формат!\nПример: <b>25.12.2025 18:00</b>", parse_mode='HTML')
                    db_actions.set_user_system_key(user_id, "index", 19)

            elif code == 20:
                try:
                    if user_input.strip() == "0":
                        bot.send_message(user_id, "❌ Удаление отменено")
                        db_actions.set_user_system_key(user_id, "index", None)
                    remind_id = int(user_input)
                    if not remind_id:
                        bot.send_message(user_id, "❌ Ошибка! Введите ID напоминания")
                        return
                    else:
                        check_remind = db_actions.reminder_is_exist(user_id, remind_id)
                        if not check_remind:
                            bot.send_message(user_id, "❌ Напоминание не найдено!")
                            return
                        else:
                            db_actions.mark_reminder_as_unactive(user_id, remind_id)
                            bot.send_message(user_id, "✅ Напоминание удалено!")
                            db_actions.set_user_system_key(user_id, "index", None)

                except:
                    bot.send_message(user_id, "❌ Ошибка! Введите ID напоминания")

            elif code == 21:
                question_ids = db_actions.get_user_system_key(user_id, "pending_questions")
                current_idx = db_actions.get_user_system_key(user_id, "current_question_index")
                question_id = question_ids[current_idx]
                if len(user_input) > 120:
                    bot.send_message(user_id, "<b>❌ Превышение лимита символов!</b>\n\n"
                    "Максимум: 120 символов", parse_mode='HTML')
                    return
                else:
                    db_actions.add_user_answer(user_id, question_id, user_input)
                    if current_idx + 1 < len(question_ids):
                        next_question = db_actions.get_question_by_id(question_ids[current_idx + 1])
                        db_actions.set_user_system_key(user_id, "current_question_index", current_idx + 1)
                        bot.send_message(
                            user_id,
                            f"✅ Ответ сохранен!\n\n"
                            f"<b>Следующий вопрос:</b>\n\n"
                            f"{current_idx + 2}/{len(question_ids)}. {next_question[1]}\n\n"
                            "Введите ваш ответ:",
                            parse_mode='HTML'
                        )
                    else:
                        bot.send_message(user_id, "✅ Вы ответили на все вопросы! Спасибо!")
                        db_actions.set_user_system_key(user_id, "index", None)

            elif code == 22:
                if len(user_input) > 120:
                    bot.send_message(user_id, "<b>❌ Превышение лимита символов!</b>\n\n"
                    "Максимум: 120 символов", parse_mode='HTML')
                    return
                else:
                    pressure = db_actions.get_user_system_key(user_id, "now_pressure")
                    db_actions.add_pressure_user(user_id, pressure, user_input)
                    bot.send_message(user_id, "✅ Данные записаны!")
                    db_actions.set_user_system_key(user_id, "index", None)

            elif code == 23:
                try:
                    days = list(set([d.strip() for d in user_input.split(',')]))
                    if all(day.isdigit() and 1 <= int(day) <= 7 for day in days):
                        remind_text = db_actions.get_user_system_key(user_id, "remind")
                        time_remind = db_actions.get_user_system_key(user_id, "time_remind")
                        
                        if db_actions.add_reminder(
                            user_id,
                            remind_text,
                            time_remind,
                            'custom',
                            ','.join(days)
                        ):
                            bot.send_message(user_id, "✅ Повторение напоминания установлено!")
                        else:
                            bot.send_message(user_id, "❌ Ошибка при создании напоминания")
                    else:
                        bot.send_message(user_id, "❌ Введите числа от 1 до 7 через запятую")
                except Exception as e:
                    print(f"Error setting custom days: {e}")
                    bot.send_message(user_id, "❌ Ошибка при обработке дней")
                db_actions.set_user_system_key(user_id, "index", None)

            elif code == 24:
                try:
                    if int(user_input):
                        db_actions.set_user_system_key(user_id, "question_id", user_input)
                        bot.send_message(user_id, "Введите текст вопроса")
                        db_actions.set_user_system_key(user_id, "index", 25)
                    else:
                        bot.send_message(user_id, "❌ Ошибка")
                except Exception as e:
                    print(f"Error: {e}")

            elif code == 25:
                question_id = db_actions.get_user_system_key(user_id, "question_id")
                if len(user_input) > 120:
                    bot.send_message(user_id, "<b>❌ Превышение лимита символов!</b>\n\n"
                    "Максимум: 120 символов", parse_mode='HTML')
                    return
                else:
                    db_actions.update_user_question(user_input, question_id, user_id)
                    bot.send_message(user_id, "Вопрос обновлен!")
                    db_actions.set_user_system_key(user_id, "index", None)

    def check_reminders():
        while True:
            try:
                current_time = int(time.time())
                reminders = db_actions.get_user_remind(current_time)
                
                for reminder in reminders:
                    try:
                        bot.send_message(
                            reminder['user_id'],
                            f"🔔 Напоминание: {reminder['reminder']}"
                        )
                    except Exception as e:
                        continue
            
                time.sleep(1)
            except Exception as e:
                time.sleep(1)

    # Запускаем функцию check_reminders в отдельном потоке
    try:
        global reminder_thread
        reminder_thread = threading.Thread(target=check_reminders, daemon=True)
        reminder_thread.start()
    except Exception as e:
        pass

    # Добавляем проверку состояния потока
    def check_thread_status():
        global reminder_thread
        while True:
            if not reminder_thread.is_alive():
                try:
                    reminder_thread = threading.Thread(target=check_reminders, daemon=True)
                    reminder_thread.start()
                except Exception as e:
                    pass
            time.sleep(5)

    # Запускаем мониторинг состояния потока
    threading.Thread(target=check_thread_status, daemon=True).start()
    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(f'{work_dir}/{config_name}', os_type)
    db = DB(config.get_config()['db_file_name'], Lock())
    db_actions = DbAct(db, config, config.get_config()['xlsx_path'])
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()