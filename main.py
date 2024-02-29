#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import os
import platform
import telebot
from threading import Lock
from backend import TempUserData, DbAct
from config_parser import ConfigParser
from db import DB
from frontend import Bot_inline_btns

####################################################################
config_name = 'secrets.json'
####################################################################


def main():
    @bot.message_handler(commands=['start'])
    def start_message(message):
        user_id = message.chat.id
        db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                            f'@{message.from_user.username}')
        buttons = Bot_inline_btns()
        bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}, я KeyShop Bot, я помогу тебе купить товары', reply_markup=buttons.msg_buttons())


    @bot.message_handler(commands=['tovar'])
    def tovar_msg(message):
        user_id = message.chat.id
        if db_actions.user_is_existed(user_id):
            buttons = Bot_inline_btns()
            bot.send_message(message.chat.id, 'Картинка', reply_markup=buttons.tovar_bnts())
            bot.send_photo(message.chat.id, 'Описание')
        else:
            bot.send_photo(message.chat.id, 'Введите /start для запуска бота')

    @bot.message_handler(content_types=['text'])
    def text_message(message):
        user_id = message.chat.id
        if db_actions.user_is_existed(user_id):
            buttons = Bot_inline_btns()
            if message.text == 'Профиль':
                bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!', reply_markup=buttons.profile_btns())
            elif message.text == 'Мои покупки':
                bot.send_message(message.chat.id, 'Ваши покупки:\n1. Back4Blood')
            elif message.text == 'Каталог продуктов':
                bot.send_message(message.chat.id, 'Выберите действие', reply_markup=buttons.product_catalog_btns())
            elif message.text == 'Поддержка':
                bot.send_message(message.chat.id, 'Выберите действие', reply_markup=buttons.support_btns())
            elif message.text == 'Наши контакты':
                bot.send_message(message.chat.id, 'Наши контакты')
            elif message.text == 'FAQ':
                bot.send_message(message.chat.id, 'FAQ')
        else:
            bot.send_photo(message.chat.id, 'Введите /start для запуска бота')
    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(f'{work_dir}/{config_name}', os_type)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    db_actions = DbAct(db, config)
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
