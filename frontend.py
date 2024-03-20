#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
from telebot import types
from textwrap import wrap
#####################################


class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=2)

    # def start_btns(self):
    #     gift = types.InlineKeyboardButton('Получить подарок🎁', callback_data='take_gift')
    #     write = types.InlineKeyboardButton('Написать продавцу✍🏼', callback_data='write_manager')
    #     self.__markup.add(gift, write)
    #     return self.__markup

    def start_buttons(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        product_catalog = types.KeyboardButton('🗂 Посмотреть доступные тесты')
        keyboard.add(product_catalog)
        return keyboard

    def categories_btns(self, data):
        data.append(('<main>', '⚙️ В главное меню'))
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            btn = types.InlineKeyboardButton(i[1], callback_data=f'categories{i[0]}')
            markup.add(btn)
        return markup

    def admin_btns(self):
        btn = types.InlineKeyboardButton('синхронизировать', callback_data=f'sync')
        self.__markup.add(btn)
        return self.__markup

