#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
from datetime import datetime
import os
import platform
import time
import telebot
import random
from telebot import types
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
        s += f'{i[0]} - {i[1]}\n'
    return s

def start_menu(message, buttons):
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAED4RZl5OeQu_YY_4FY1bfDeW-bfZobdQACXEYAAshAgEmc8EyBI3PWVDQE', reply_markup=buttons.msg_buttons())


def main():
    @bot.message_handler(commands=['start'])
    def start_message(message):
        user_id = message.chat.id
        db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                            f'@{message.from_user.username}')
        buttons = Bot_inline_btns()
        bot.send_message(message.chat.id,
                         f'Привет {message.from_user.first_name}👋\n'
                         f'{config.get_config()["start_msg"]}',
                         reply_markup=buttons.msg_buttons())

    @bot.message_handler(commands=['admin'])
    def tovar_msg(message):
        command = message.text.replace('/', '')
        user_id = message.chat.id
        if db_actions.user_is_existed(user_id):
            buttons = Bot_inline_btns()
            if db_actions.user_is_admin(user_id):
                if command == 'admin':
                    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}!\nТекущий шаг скидки {config.get_config()["step_sale"]}, процент за шаг {config.get_config()["percent_sale"]}',
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
                        bot.send_message(message.chat.id,
                                         f'Отправьте ID подкатегории\nДоступные варианты:\n{get_subcot()}')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
                elif status == 4:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][1][4] = user_input
                        temp_user_data.temp_data(user_id)[user_id][0] = 12
                        bot.send_message(message.chat.id, 'Отправьте превью')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
                elif status == 5:
                    if user_input is not None:
                        if db_actions.check_product_id_exist(user_input):
                            temp_user_data.temp_data(user_id)[user_id][2] = user_input
                            temp_user_data.temp_data(user_id)[user_id][0] = None
                            bot.send_message(message.chat.id, 'Что вы хотите изменить/добавить✏️',
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
                        old_keys = db_actions.get_all_keys_product(temp_user_data.temp_data(user_id)[user_id][2])
                        new_keys = old_keys + f',{user_input}'
                        new_keys = ','.join(set(new_keys.split(',')))
                        db_actions.update_product(new_keys, 'key',
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
                elif status == 11:
                    if user_input is not None:
                        db_actions.update_product(user_input, 'preview',
                                                  temp_user_data.temp_data(user_id)[user_id][2])
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(user_id, '✅Операция завершена успешно✅')
                    else:
                        bot.send_message(user_id, '❌Это не текст❌')
                elif status == 12:
                    if user_input is not None:
                        temp_user_data.temp_data(user_id)[user_id][1][5] = user_input
                        temp_user_data.temp_data(user_id)[user_id][0] = 18
                        bot.send_message(message.chat.id, 'Товар будет с привязкой? (да или нет)')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
                elif status == 13:
                    if user_input is not None:
                        config.change_contacts(user_input)
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(message.chat.id, '✅Изменения успешно сохранены✅')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
                elif status == 14:
                    if user_input is not None:
                        config.change_faq(user_input)
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(message.chat.id, '✅Изменения успешно сохранены✅')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
                elif status == 15:
                    if user_input is not None:
                        config.change_start_msg(user_input)
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(message.chat.id, '✅Изменения успешно сохранены✅')
                    else:
                        bot.send_message(message.chat.id, '❌Это не текст❌')
                elif status == 16:
                    try:
                        config.change_step(int(user_input))
                        temp_user_data.temp_data(user_id)[user_id][0] = 17
                        bot.send_message(message.chat.id, 'Введите процент скидки')
                    except:
                        bot.send_message(message.chat.id, '❌Это не число❌')
                elif status == 17:
                    try:
                        config.change_percent(int(user_input))
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(message.chat.id, '✅Изменения успешно сохранены✅')
                    except:
                        bot.send_message(message.chat.id, '❌Это не число❌')
                elif status == 18:
                    try:
                        print(user_input)
                        if user_input.lower() == 'да':
                            with_reference = True
                            print(3)
                        elif user_input.lower() == 'нет':
                            with_reference = False
                        else:
                            raise
                        temp_user_data.temp_data(user_id)[user_id][1][6] = with_reference
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        db_actions.add_one_product(temp_user_data.temp_data(user_id)[user_id][1])
                        bot.send_message(message.chat.id, '✅Товар успешно добавлен✅')
                    except:
                        bot.send_message(message.chat.id, '❌Вы ввели неверное значение❌')
            else:
                if message.text == 'Профиль👤':
                    bot.send_message(message.chat.id,
                                     f'Привет, {message.from_user.first_name} {message.from_user.last_name}!',
                                     reply_markup=buttons.profile_btns())
                elif message.text == 'Мои покупки🛒':
                    data = db_actions.get_preview_from_sales(user_id)
                    bot.send_message(message.chat.id, 'Ваши покупки', reply_markup=buttons.purchased_btns(data))
                elif message.text == 'Назад🔙':
                    start_menu(message, buttons)
                elif message.text == 'Каталог продуктов🗂':
                    categories = db_actions.get_categories()
                    bot.send_message(message.chat.id, 'Выберите категорию✅',
                                     reply_markup=buttons.categories_btns(categories))
                elif message.text == 'Поддержка👨‍💻':
                    bot.send_message(message.chat.id, 'Выберите действие✅', reply_markup=buttons.support_btns())
                elif message.text == 'Наши контакты👥':
                    bot.send_message(message.chat.id, f'Наши контакты:\n{config.get_config()["contacts"]}')
                elif message.text == 'FAQℹ️':
                    bot.send_message(message.chat.id, f'FAQ:\n{config.get_config()["FAQ"]}')
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
                        bot.send_message(call.message.chat.id, '🔑Введите новый ключ🔑')
                    elif command[10:] == '4':
                        temp_user_data.temp_data(user_id)[user_id][0] = 9
                        bot.send_message(call.message.chat.id,
                                         f'✉️Введите новую подкатегорию для товара✉️\nДоступные варианты:\n{get_subcot()}')
                    elif command[10:] == '5':
                        temp_user_data.temp_data(user_id)[user_id][0] = 10
                        bot.send_message(call.message.chat.id, '🪪Введите новое описание🪪')
                    elif command[10:] == '6':
                        temp_user_data.temp_data(user_id)[user_id][0] = 11
                        bot.send_message(call.message.chat.id, '🪪Введите новое превью🪪')
                elif command == 'changecontact':
                    bot.send_message(call.message.chat.id, '👤Введите новый контакт👤')
                    temp_user_data.temp_data(user_id)[user_id][0] = 13
                elif command == 'changefaq':
                    bot.send_message(call.message.chat.id, '💎Введите новый FAQ💎')
                    temp_user_data.temp_data(user_id)[user_id][0] = 14
                elif command == 'changestartmsg':
                    bot.send_message(call.message.chat.id, '✉️Введите новое стартовое сообщение✉️')
                    temp_user_data.temp_data(user_id)[user_id][0] = 15
                elif command == 'changesale':
                    temp_user_data.temp_data(user_id)[user_id][0] = 16
                    bot.send_message(call.message.chat.id, '✉️Введите шаг скидки✉️')
            if command[:10] == 'categories':
                if command[10:] == '<main>':
                    bot.delete_message(user_id, message_id)
                    start_menu(call.message, buttons)
                else:
                    temp_user_data.temp_data(user_id)[user_id][5] = command[10:]
                    subcategories = db_actions.get_sub_by_id_categories(command[10:])
                    bot.edit_message_text('🪪Выберите подкатегорию🪪', user_id, message_id,
                                          reply_markup=buttons.subcategories_btns(subcategories))
            elif command[:13] == 'subcategories':
                if command[13:] == '<back>':
                    categories = db_actions.get_categories()
                    bot.edit_message_text('🪪Выберите категорию🪪', user_id, message_id,
                                          reply_markup=buttons.categories_btns(categories))
                elif command[13:] == '<main>':
                    bot.delete_message(user_id, message_id)
                    start_menu(call.message, buttons)
                else:
                    temp_user_data.temp_data(user_id)[user_id][6] = command[13:]
                    bot.edit_message_text('🪪Выберите тип товара (с привязкой или без)🪪', user_id, message_id,
                                          reply_markup=buttons.reference_btns())
            elif command[:9] == 'reference':
                if command[9:] == '<back>':
                    subcategories = db_actions.get_sub_by_id_categories(temp_user_data.temp_data(user_id)[user_id][5])
                    bot.edit_message_text('🪪Выберите подкатегорию🪪', user_id, message_id,
                                          reply_markup=buttons.subcategories_btns(subcategories))
                elif command[9:] == '<main>':
                    bot.delete_message(user_id, message_id)
                    start_menu(call.message, buttons)
                else:
                    products = db_actions.get_products_preview(temp_user_data.temp_data(user_id)[user_id][6], command[9:])
                    bot.edit_message_text('🪪Выберите товар🪪', user_id, message_id,
                                          reply_markup=buttons.products_btns(products))
            elif command[:8] == 'products':
                if command[8:] == '<back>':
                    if temp_user_data.temp_data(user_id)[user_id][3] is not None:
                        bot.delete_message(user_id, temp_user_data.temp_data(user_id)[user_id][3])
                        temp_user_data.temp_data(user_id)[user_id][3] = None
                    bot.edit_message_text('🪪Выберите тип товара (с привязкой или без)🪪', user_id, message_id,
                                          reply_markup=buttons.reference_btns())
                elif command[8:] == '<main>':
                    if temp_user_data.temp_data(user_id)[user_id][3] is not None:
                        bot.delete_message(user_id, temp_user_data.temp_data(user_id)[user_id][3])
                        temp_user_data.temp_data(user_id)[user_id][3] = None
                    bot.delete_message(user_id, message_id)
                    start_menu(call.message, buttons)
                else:
                    product = db_actions.get_product_by_id(command[8:])
                    if temp_user_data.temp_data(user_id)[user_id][3] is not None:
                        bot.delete_message(user_id, temp_user_data.temp_data(user_id)[user_id][3])
                    keys_left = len(db_actions.get_all_keys_product(command[8:]).split(','))
                    temp_user_data.temp_data(user_id)[user_id][3] = bot.send_photo(photo=product[0],
                                                                                   caption=f'💎ID товара: {command[8:]}\nКлючей осталось: {keys_left}\n📨Описание: {product[2]}\n💸Цена: {product[1]}',
                                                                                   chat_id=user_id,
                                                                                   reply_markup=buttons.buy_btns(
                                                                                       command[8:])).message_id
            elif command[:3] == 'buy':
                keys = list()
                product = db_actions.get_product_by_id_for_buy(command[3:])
                for i in product[2].split(','):
                    if i != '':
                        keys.append(i)
                if len(keys) != 0:
                    key = random.choice(keys)
                    keys.remove(key)
                    db_actions.update_product(','.join(keys), 'key', command[3:])
                    price = product[1] - (int(product[1] / 100) * ((product[1] // config.get_config()['step_sale']) * config.get_config()['percent_sale']))
                    temp_user_data.temp_data(user_id)[user_id][7] = bot.send_invoice(user_id, title=f'Активационный ключ для {product[0]}', description=product[3],
                                     invoice_payload=f'{product[0]}ɹ{key}ɹ{command[3:]}', provider_token=payments, currency='RUB',
                                     prices=[types.LabeledPrice('Оплата товара', price * 100)]).message_id
                else:
                    bot.answer_callback_query(call.id, "Ключей нет в наличии", show_alert=True)
            elif command[:9] == 'purchased':
                if command[9:] == '<main>':
                    if temp_user_data.temp_data(user_id)[user_id][4] is not None:
                        bot.delete_message(user_id, temp_user_data.temp_data(user_id)[user_id][4])
                        temp_user_data.temp_data(user_id)[user_id][4] = None
                    bot.delete_message(user_id, message_id)
                    start_menu(call.message, buttons)
                else:
                    content = db_actions.get_sale_by_id(command[9:])
                    if temp_user_data.temp_data(user_id)[user_id][4] is not None:
                        bot.delete_message(user_id, temp_user_data.temp_data(user_id)[user_id][4])
                    temp_user_data.temp_data(user_id)[user_id][4] = bot.send_message(user_id, text=content).message_id
        else:
            bot.send_message(user_id, 'Введите /start для запуска бота')

    @bot.pre_checkout_query_handler(func=lambda query: True)
    def checkout(message):
        user_id = message.from_user.id
        tg_nick = message.from_user.username
        data = message.invoice_payload.split('ɹ')
        price = int(message.total_amount / 100)
        payment_status = bot.answer_pre_checkout_query(message.id, ok=True,
                                      error_message="Оплата не прошла - попробуйте, пожалуйста, еще раз,"
                                                    "или свяжитесь с администратором бота.")
        if not payment_status:
            keys = list()
            timee = time.time()
            sheet.add_sale([datetime.utcfromtimestamp(timee).strftime('%Y-%m-%d %H:%M'), data[0], price, 'Отклонена', f'@{tg_nick}', 'Нет'])
            db_actions.add_sale([timee, data[0], price, False, f'@{tg_nick}', user_id, data[1], data[2]])
            if temp_user_data.temp_data(user_id)[user_id][7] is not None:
                bot.delete_message(user_id, temp_user_data.temp_data(user_id)[user_id][7])
                temp_user_data.temp_data(user_id)[user_id][7] = None
            product = db_actions.get_product_by_id_for_buy(data[2])
            for i in product[2].split(','):
                if i != '':
                    keys.append(i)
            keys.append(data[1])
            db_actions.update_product(','.join(keys), 'key', product[2])

    @bot.message_handler(content_types=['successful_payment'])
    def got_payment(message):
        user_id = message.from_user.id
        tg_nick = message.from_user.username
        data = message.successful_payment.invoice_payload.split('ɹ')
        price = int(message.successful_payment.total_amount / 100)
        timee = time.time()
        if temp_user_data.temp_data(user_id)[user_id][7] is not None:
            bot.delete_message(user_id, temp_user_data.temp_data(user_id)[user_id][7])
            temp_user_data.temp_data(user_id)[user_id][7] = None
        db_actions.add_sale([timee, data[0], price, True, f'@{tg_nick}', user_id, data[1], data[2]])
        sheet.add_sale([datetime.utcfromtimestamp(timee).strftime('%Y-%m-%d %H:%M'), data[0], price, 'Успешно', f'@{tg_nick}', data[1]])
        bot.send_message(user_id, f'Оплата совершена успешно, полная информация о вашей покупке продублирована в '
                                          f'Профиль>Мои покупки\nВаш лицензионный ключ: {data[1]}')


    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(f'{work_dir}/{config_name}', os_type)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    sheet = Excell(db)
    db_actions = DbAct(db, config)
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    payments = config.get_config()['payment_api']
    main()
