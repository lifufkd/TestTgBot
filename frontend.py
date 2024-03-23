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
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        product_catalog = types.InlineKeyboardButton('🗂 Посмотреть доступные тесты', callback_data='tret')
        keyboard.add(product_catalog)
        return keyboard

    def start_test_btn(self, text, test_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton(text, callback_data=f'start_test{test_id}')
        markup.add(btn)
        return markup

    def contiue_test_btn(self, text, test_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton(text, callback_data=f'continue{test_id}')
        markup.add(btn)
        return markup

    def end_test_btn(self, test_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton('Итоги теста', callback_data=f'end{test_id}')
        markup.add(btn)
        return markup

    def admin_btns(self):
        btn = types.InlineKeyboardButton('синхронизировать', callback_data=f'sync')
        self.__markup.add(btn)
        return self.__markup

    def answer_btns(self, quanity):
        markup = types.InlineKeyboardMarkup(row_width=4)
        for i in range(len(quanity)):
            btn = types.InlineKeyboardButton(quanity[i], callback_data=f'answer{i+1}')
            markup.add(btn)
        return markup

