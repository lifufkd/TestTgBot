#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
from datetime import datetime
import os
import platform
import telebot
import random
import threading
from threading import Lock
from backend import TempUserData, DbAct, Excell
from config_parser import ConfigParser
from db import DB
from frontend import Bot_inline_btns
####################################################################
config_name = 'secrets.json'
####################################################################


def get_subcot():
    s = ''
    data = db_actions.get_subcategories()
    for i in data:
        s += f'{i[0]}. {i[1]}\n'
    return s

def get_preview():
    s = ''
    data = db_actions.get_all_products_preview()
    for i in data:
        s += f'{i[0]}. {i[1]} * {i[2]}\n'
    return s

def get_category():
    s = ''
    data = db_actions.get_categories()
    for i in data:
        s += f'{i[0]}. {i[1]}\n'
    return s


def main():
    @bot.message_handler(commands=['start'])
    def start_message(message):
        user_id = message.chat.id
        db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                            f'@{message.from_user.username}')
        buttons = Bot_inline_btns()
        bot.send_message(message.chat.id,
                         f'Привет {message.from_user.first_name}👋\n'
                         'Я помогу вам найти тест!',
                         reply_markup=buttons.start_buttons())

    @bot.message_handler(commands=['admin'])
    def tovar_msg(message):
        command = message.text.replace('/', '')
        user_id = message.chat.id
        if db_actions.user_is_existed(user_id):
            buttons = Bot_inline_btns()
            if db_actions.user_is_admin(user_id):
                if command == 'admin':
                    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}!\n',
                                     reply_markup=buttons.admin_btns())
        else:
            bot.send_message(message.chat.id, 'Введите /start для запуска бота')

    @bot.message_handler(content_types=['text', 'photo'])
    def text_message(message):
        photo = message.photo
        user_input = message.text
        user_id = message.chat.id
        if db_actions.user_is_existed(user_id):
            buttons = Bot_inline_btns()
            if temp_user_data.temp_data(user_id)[user_id][0] is not None:
                status = temp_user_data.temp_data(user_id)[user_id][0]
                if status == 0:
                    pass
            else:
                if message.text == '👤 Профиль':
                    temp_user_data.temp_data(user_id)[user_id][7] = bot.send_message(message.chat.id,
                                     f'Привет, {message.from_user.first_name}!\nВаш ID: {user_id}',
                                     reply_markup=buttons.profile_btns()).message_id
                elif message.text == '🗂 Каталог продуктов':
                    categories = db_actions.get_categories()
                    temp_user_data.temp_data(user_id)[user_id][6] = bot.send_message(message.chat.id, config.get_config()['text_category'],
                                     reply_markup=buttons.categories_btns(categories), parse_mode='HTML').message_id
                elif message.text == '👨‍💻 Поддержка':
                    temp_user_data.temp_data(user_id)[user_id][7] = bot.send_message(message.chat.id, 'Выберите действие✅', reply_markup=buttons.support_btns()).message_id
        else:
            bot.send_message(message.chat.id, 'Введите /start для запуска бота')

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        command = call.data
        tg_nick = call.message.chat.username
        message_id = call.message.id
        user_id = call.message.chat.id
        if db_actions.user_is_existed(user_id):
            buttons = Bot_inline_btns()
            if db_actions.user_is_admin(user_id):
                if command == 'sync':
                    db_actions.update_config(sheet.config_excell())
                    bot.send_message(user_id, 'Обновление успешно завершено!')
        else:
            bot.send_message(user_id, 'Введите /start для запуска бота')

    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    config = ConfigParser(config_name, os_type)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    sheet = Excell(db, config)
    db_actions = DbAct(db, config)
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
