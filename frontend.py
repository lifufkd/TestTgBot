#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
from telebot import types
#####################################


class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=2)

    def first_btns(self, data):
        markup = types.InlineKeyboardMarkup(row_width=len(data))
        for i in data:
            btn3 = types.InlineKeyboardButton(i[1], callback_data=f'test{i[0]}')
            markup.add(btn3)
        return markup

    def start_buttons(self, text):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        product_catalog = types.InlineKeyboardButton(f'{text}', callback_data='tret')
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

    def end_test_btn(self, test_id, text_end, text_again, stat):
        markup = types.InlineKeyboardMarkup(row_width=1)
        if stat:
            btn = types.InlineKeyboardButton(text_again, callback_data=f'again{test_id}')
            btn1 = types.InlineKeyboardButton('Завершить тест', callback_data=f'end{test_id}')
            markup.add(btn, btn1)
        else:
            btn1 = types.InlineKeyboardButton('Завершить тест', callback_data=f'end{test_id}')
            markup.add(btn1)
        return markup

    def admin_btns(self):
        btn = types.InlineKeyboardButton('синхронизировать', callback_data=f'sync')
        self.__markup.add(btn)
        return self.__markup

    def answer_btns(self, quanity, qe):
        markup = types.InlineKeyboardMarkup(row_width=int(qe))
        btn = types.InlineKeyboardButton(quanity[0], callback_data=f'answer{1}')
        btn1 = types.InlineKeyboardButton(quanity[1], callback_data=f'answer{2}')
        btn2 = types.InlineKeyboardButton(quanity[2], callback_data=f'answer{3}')
        btn3 = types.InlineKeyboardButton(quanity[3], callback_data=f'answer{4}')
        markup.add(btn, btn1, btn2, btn3)
        return markup

