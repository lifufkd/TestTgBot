#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################

import telebot
from telebot import types


#####################################
class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=1)

    # def start_btns(self):
    #     gift = types.InlineKeyboardButton('Получить подарок🎁', callback_data='take_gift')
    #     write = types.InlineKeyboardButton('Написать продавцу✍🏼', callback_data='write_manager')
    #     self.__markup.add(gift, write)
    #     return self.__markup

    def msg_buttons(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        product_catalog = types.KeyboardButton('Каталог продуктов')
        profile = types.KeyboardButton('Профиль')
        support = types.KeyboardButton('Поддержка')
        keyboard.add(product_catalog, profile, support)
        return keyboard

    def tovar_bnts(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buy = types.KeyboardButton('Купить')
        download_dist = types.KeyboardButton('Скачать дистрибутив')
        instruction = types.KeyboardButton('Инструкция по активации')
        keyboard.add(buy, download_dist, instruction)
        return keyboard

    def categories_btns(self):
        categories = types.InlineKeyboardButton('Список категорий', callback_data='category')
        self.__markup.add(categories)
        return self.__markup

    def podcategories_btns(self):
        podcategories = types.InlineKeyboardButton('Список подкатегорий', callback_data='podcategory')
        self.__markup.add(podcategories)
        return self.__markup

    def tovar_btns(self):
        tovar = types.InlineKeyboardButton('Список товаров внутри подкатегорий', callback_data='tovary_in_podcategories')
        self.__markup.add(tovar)
        return self.__markup


    def profile_btns(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        my_buys = types.KeyboardButton('Мои покупки')
        keyboard.add(my_buys)
        return keyboard

    def support_btns(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        our_contacts = types.KeyboardButton('Наши контакты')
        FAQ = types.KeyboardButton('FAQ')
        keyboard.add(our_contacts, FAQ)
        return keyboard



