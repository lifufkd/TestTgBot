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


def get_subcot():
    s = ''
    data = db_actions.get_subcategories()
    for i in data:
        s += f'{i[0]} - {i[1]}\n'
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
                         f'Я KeyShop Bot🤖',
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
                    if photo is not None:
                        photo_id = photo[-1].file_id
                        photo_file = bot.get_file(photo_id)
                        photo_bytes = bot.download_file(photo_file.file_path)
                        temp_user_data.temp_data(user_id)[user_id][1][0] = photo_bytes
                        temp_user_data.temp_data(user_id)[user_id][0] = 1
                        bot.send_message(message.chat.id, '💸Отправьте цену товара💸')
                    else:
                        bot.send_message(message.chat.id, '❌Это не фото❌')
                elif status == 1:
                    if user_input is not None:
                        try:
                            temp_user_data.temp_data(user_id)[user_id][1][1] = int(user_input)
                            temp_user_data.temp_data(user_id)[user_id][0] = 2
                            bot.send_message(message.chat.id, 'Отправьте активационный ключ🔑')
                        except:
                            bot.send_message(message.chat.id, '❌Сумма неверна❌')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
                elif status == 2:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][1][2] = user_input
                        temp_user_data.temp_data(user_id)[user_id][0] = 3
                        bot.send_message(message.chat.id, 'Введите описание товара📨')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
                elif status == 3:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][1][3] = user_input
                        temp_user_data.temp_data(user_id)[user_id][0] = 4
                        bot.send_message(message.chat.id, f'Отправьте ID подкатегории\nДоступные варианты:\n{get_subcot()}')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
                elif status == 4:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][1][4] = user_input
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        db_actions.add_one_product(temp_user_data.temp_data(user_id)[user_id][1])
                        bot.send_message(message.chat.id, '✅Товар успешно добавлен✅')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
                elif status == 5:
                    if user_input is not None:
                        if db_actions.check_product_id_exist(user_input):
                            temp_user_data.temp_data(user_id)[user_id][2] = user_input
                            temp_user_data.temp_data(user_id)[user_id][0] = None
                            bot.send_message(message.chat.id, 'Что вы хотите изменить✏️',
                                             reply_markup=buttons.change_btns())
                        else:
                            bot.send_message(message.chat.id, '❌ID продукта не существует❌')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
                elif status == 6:
                    if user_input is not None:
                        try:
                            db_actions.update_product(int(user_input), 'price',
                                                      temp_user_data.temp_data(user_id)[user_id][2])
                            temp_user_data.temp_data(user_id)[user_id][0] = None
                            bot.send_message(user_id, '✅Операция завершена успешно✅')
                        except:
                            bot.send_message(user_id, '❌Сумма неверна❌')
                    else:
                        bot.send_message(user_id, '❌Это не текст❌')
                elif status == 7:
                    if photo is not None:
                        photo_id = photo[-1].file_id
                        photo_file = bot.get_file(photo_id)
                        photo_bytes = bot.download_file(photo_file.file_path)
                        db_actions.update_product(photo_bytes, 'photo',
                                                  temp_user_data.temp_data(user_id)[user_id][2])
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(user_id, '✅Операция завершена успешно✅')
                    else:
                        bot.send_message(user_id, '❌Это не фото❌')
                elif status == 8:
                    if user_input is not None:
                        db_actions.update_product(user_input, 'key',
                                                  temp_user_data.temp_data(user_id)[user_id][2])
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(user_id, '✅Операция завершена успешно✅')
                    else:
                        bot.send_message(user_id, '❌Это не текст❌')
                elif status == 9:
                    if user_input is not None:
                        db_actions.update_product(user_input, 'category',
                                                  temp_user_data.temp_data(user_id)[user_id][2])
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(user_id, '✅Операция завершена успешно✅')
                    else:
                        bot.send_message(user_id, '❌Это не текст❌')
                elif status == 10:
                    if user_input is not None:
                        db_actions.update_product(user_input, 'description',
                                                  temp_user_data.temp_data(user_id)[user_id][2])
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(user_id, '✅Операция завершена успешно✅')
                    else:
                        bot.send_message(user_id, '❌Это не текст❌')
            else:
                if message.text == 'Профиль👤':
                    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}!',
                                     reply_markup=buttons.profile_btns())
                elif message.text == 'Мои покупки🛒':
                    bot.send_message(message.chat.id, 'Ваши покупки:\n1. Back4Blood')
                elif message.text == 'Назад🔙':
                    bot.send_message(message.chat.id,
                                     f'Привет {message.from_user.first_name}👋\n'
                                     f'Я KeyShop Bot🤖',
                                     reply_markup=buttons.msg_buttons())
                elif message.text == 'Каталог продуктов🗂':
                    categories = db_actions.get_categories()
                    bot.send_message(message.chat.id, 'Выберите категорию✅', reply_markup=buttons.categories_btns(categories))
                elif message.text == 'Поддержка👨‍💻':
                    bot.send_message(message.chat.id, 'Выберите действие✅', reply_markup=buttons.support_btns())
                elif message.text == 'Наши контакты👥':
                    bot.send_message(message.chat.id, 'Наши контакты')
                elif message.text == 'FAQℹ️':
                    bot.send_message(message.chat.id, 'FAQ')
        else:
            bot.send_message(message.chat.id, 'Введите /start для запуска бота')

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        command = call.data
        user_input = call.message.text
        photo = call.message.photo
        message_id = call.message.id
        user_id = call.message.chat.id
        if db_actions.user_is_existed(user_id):
            buttons = Bot_inline_btns()
            if db_actions.user_is_admin(user_id):
                if command == 'addproduct':
                    temp_user_data.temp_data(user_id)[user_id][0] = 0
                    bot.send_message(call.message.chat.id, 'Отправьте фото товара🖼')
                elif command == 'importproducts':
                    db_actions.update_products_from_excell(sheet.products_excell())
                elif command == 'importcategories':
                    db_actions.update_categories_from_excell(sheet.categories_excell())
                elif command == 'importsubcategories':
                    db_actions.update_subcategories_from_excell(sheet.subcategories_excell())
                elif command == 'changeproduct':
                    temp_user_data.temp_data(user_id)[user_id][0] = 5
                    bot.send_message(call.message.chat.id, '💎Введите ID товара💎')
                elif command[:10] == 'сhangecart':
                    if command[10:] == '1':
                        temp_user_data.temp_data(user_id)[user_id][0] = 6
                        bot.send_message(call.message.chat.id, '💸Введите новую цену💸')
                    elif command[10:] == '2':
                        temp_user_data.temp_data(user_id)[user_id][0] = 7
                        bot.send_message(call.message.chat.id, '🖼Введите новую обложку🖼')
                    elif command[10:] == '3':
                        temp_user_data.temp_data(user_id)[user_id][0] = 8
                        bot.send_message(call.message.chat.id, '🔑Введите новую ключ🔑')
                    elif command[10:] == '4':
                        temp_user_data.temp_data(user_id)[user_id][0] = 9
                        bot.send_message(call.message.chat.id, f'✉️Введите новую подкатегорию для товара✉️\nДоступные варианты:\n{get_subcot()}')
                    elif command[10:] == '5':
                        temp_user_data.temp_data(user_id)[user_id][0] = 10
                        bot.send_message(call.message.chat.id, '🪪Введите новое описание🪪')
            if command[:10] == 'categories':
                subcategories = db_actions.get_sub_by_id_categories(command[10:])
                bot.edit_message_text('🪪Выберите подкатегорию🪪', user_id, message_id, reply_markup=buttons.subcategories_btns(subcategories))
            elif command[:13] == 'subcategories':
                if command[13:] == '<back>':
                    categories = db_actions.get_categories()
                    bot.edit_message_text('🪪Выберите категорию🪪', user_id, message_id,
                                     reply_markup=buttons.categories_btns(categories))
                elif command == 'addcontact':
                    bot.send_message(call.message.chat.id, '👤Введите новый контакт👤')
                    temp_user_data.temp_data(user_id)[user_id][0] = 13
                elif command == 'addfaq':
                    bot.send_message(call.message.chat.id, 'ℹ️Введите новый FAQℹ️')
                    temp_user_data.temp_data(user_id)[user_id][0] = 14
                else:
                    products = db_actions.get_products_by_id(command[13:])
                    for i in products:
                        bot.send_photo(user_id, photo=i[1], caption=f'💎ID товара: {i[0]}\n🔑Ключ: {i[3]}\n📨Описание: {i[4]}\n💸Цена: {i[2]}', reply_markup=buttons.buy_btns(i[0]))
        else:
            bot.send_message(user_id, 'Введите /start для запуска бота')

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
