#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import os
import platform
import telebot
from config_parser import ConfigParser
from frontend import Bot_inline_btns

####################################################################
config_name = 'secrets.json'
####################################################################


def main():
    @bot.message_handler(commands=['start'])
    def start_message(message):
        buttons = Bot_inline_btns()
        bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}, я KeyShop Bot, я помогу тебе купить товары', reply_markup=buttons.msg_buttons())


    @bot.message_handler(commands=['tovar'])
    def tovar_msg(message):
        buttons = Bot_inline_btns()
        bot.send_message(message.chat.id, 'Картинка', reply_markup=buttons.tovar_bnts())
        bot.send_photo(message.chat.id, 'Описание')

    @bot.message_handler(content_types=['text'])
    def text_message(message):
        buttons = Bot_inline_btns()
        if message.text == 'Профиль':
            bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!', reply_markup=buttons.profile_btns())
        elif message.text == 'Мои покупки':
            bot.send_message(message.chat.id, 'Ваши покупки:\n1. Back4Blood')
        elif message.text == 'Каталог продуктов':
            categoriies = bot.send_message(message.chat.id, 'Категории', reply_markup=buttons.categories_btns())
        elif message.text == 'Поддержка':
            bot.send_message(message.chat.id, 'Выберите действие', reply_markup=buttons.support_btns())
        elif message.text == 'Наши контакты':
            bot.send_message(message.chat.id, 'Наши контакты')
        elif message.text == 'FAQ':
            bot.send_message(message.chat.id, 'FAQ')


    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        buttons = Bot_inline_btns()
        if call.data == 'category':
            podcategoriies = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.categoriies.id, text='Подкатегории', reply_markup=buttons.podcategories_btns())
        elif call.data == 'podcategory':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.podcategoriies.id, text='Товары внутри подкатегории', reply_markup=buttons.tovar_btns())

    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(f'{work_dir}/{config_name}', os_type)
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
