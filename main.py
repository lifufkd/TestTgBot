#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import os
import platform
import telebot
from threading import Lock
from backend import TempUserData, DbAct, ExcellImport
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
        bot.send_message(message.chat.id,
                         f'Привет {message.from_user.first_name}👋\nЯ KeyShop Bot🤖\nВыбери действие снизу✅',
                         reply_markup=buttons.msg_buttons())

    @bot.message_handler(commands=['tovar', 'admin'])
    def tovar_msg(message):
        command = message.text.replace('/', '')
        user_id = message.chat.id
        if db_actions.user_is_existed(user_id):
            buttons = Bot_inline_btns()
            if command == 'tovar':
                bot.send_message(message.chat.id, 'Картинка', reply_markup=buttons.tovar_bnts())
                bot.send_message(message.chat.id, 'Описание')
            if db_actions.user_is_admin(user_id):
                if command == 'admin':
                    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}!',
                                     reply_markup=buttons.admin_btns())
        else:
            bot.send_message(message.chat.id, 'Введите <b>/start</b> для запуска бота', parse_mode='HTML')

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
                    if photo is not None:
                        photo_id = photo[-1].file_id
                        photo_file = bot.get_file(photo_id)
                        photo_bytes = bot.download_file(photo_file.file_path)
                        temp_user_data.temp_data(user_id)[user_id][1][0] = photo_bytes
                        temp_user_data.temp_data(user_id)[user_id][0] = 1
                        bot.send_message(message.chat.id, '💰Отправьте цену товара💰')
                    else:
                        bot.send_message(message.chat.id, '❌Это не фото❌')
                elif status == 1:
                    if user_input is not None:
                        try:
                            temp_user_data.temp_data(user_id)[user_id][1][1] = int(user_input)
                            temp_user_data.temp_data(user_id)[user_id][0] = 2
                            bot.send_message(message.chat.id, '🔑Отправьте активационный ключ🔑')
                        except:
                            bot.send_message(message.chat.id, '❌Сумма неверна!❌')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
                elif status == 2:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][1][2] = user_input
                        temp_user_data.temp_data(user_id)[user_id][0] = 3
                        bot.send_message(message.chat.id, '📨Введите описание товара📨')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
                elif status == 3:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][1][3] = user_input
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        db_actions.add_one_product(temp_user_data.temp_data(user_id)[user_id][1])
                        bot.send_message(message.chat.id, '✅Товар успешно добавлен✅')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
            else:
                if message.text == 'Профиль':
                    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!',
                                     reply_markup=buttons.profile_btns())
                elif message.text == 'Мои покупки':
                    bot.send_message(message.chat.id, 'Ваши покупки:\n1. Back4Blood')
                elif message.text == 'Каталог продуктов':
                    bot.send_message(message.chat.id, '✅Выберите действие✅', reply_markup=buttons.categories_btns())
                elif message.text == 'Поддержка':
                    bot.send_message(message.chat.id, '✅Выберите действие✅', reply_markup=buttons.support_btns())
                elif message.text == 'Наши контакты':
                    bot.send_message(message.chat.id, 'Наши контакты')
                elif message.text == 'FAQ':
                    bot.send_message(message.chat.id, 'FAQ')
        else:
            bot.send_message(message.chat.id, 'Введите /start для запуска бота')

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        command = call.data
        user_id = call.message.chat.id
        if db_actions.user_is_existed(user_id):
            if db_actions.user_is_admin(user_id):
                if command == 'addproduct':
                    temp_user_data.temp_data(user_id)[user_id][0] = 0
                    bot.send_message(call.message.chat.id, '🖼Отправьте фото товара🖼')
                elif command == 'importexcell':
                    pass

    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(f'{work_dir}/{config_name}', os_type)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    sheet = ExcellImport(db)
    db_actions = DbAct(db, config)
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
