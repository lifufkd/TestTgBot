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

    # def start_btns(self):
    #     gift = types.InlineKeyboardButton('Получить подарок🎁', callback_data='take_gift')
    #     write = types.InlineKeyboardButton('Написать продавцу✍🏼', callback_data='write_manager')
    #     self.__markup.add(gift, write)
    #     return self.__markup

    def msg_buttons(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        product_catalog = types.KeyboardButton('Каталог продуктов🗂')
        profile = types.KeyboardButton('Профиль👤')
        support = types.KeyboardButton('Поддержка👨‍💻')
        keyboard.add(product_catalog, profile, support)
        return keyboard

    def tovar_bnts(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buy = types.KeyboardButton('Купить💎')
        download_dist = types.KeyboardButton('Скачать дистрибутив🖥')
        instruction = types.KeyboardButton('Инструкция по активации✉️')
        keyboard.add(buy, download_dist, instruction)
        return keyboard

    def podcategories_btns(self):
        podcategories = types.InlineKeyboardButton('Список подкатегорий', callback_data='podcategory')
        self.__markup.add(podcategories)
        return self.__markup

    def tovar_btns(self):
        tovar = types.InlineKeyboardButton('Список товаров внутри подкатегорий', callback_data='tovary_in_podcategories')
        self.__markup.add(tovar)
        return self.__markup


    def profile_btns(self):
        markup = types.InlineKeyboardMarkup(row_width=1)
        my_buys = types.InlineKeyboardButton('Мои покупки🛒' , callback_data='my_buys')
        back = types.InlineKeyboardButton('Назад🔙' , callback_data='back')
        markup.add(my_buys, back)
        return markup

    def support_btns(self):
        markup = types.InlineKeyboardMarkup(row_width=1)
        my_buys = types.InlineKeyboardButton('Наши контакты👥', callback_data='our_contacts')
        FAQ = types.InlineKeyboardButton('FAQℹ️', callback_data='FAQ')
        back = types.InlineKeyboardButton('Назад🔙', callback_data='back')
        markup.add(my_buys, FAQ, back)
        return markup
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        our_contacts = types.KeyboardButton('Наши контакты👥')
        FAQ = types.KeyboardButton('FAQℹ️')
        back = types.KeyboardButton('Назад🔙')
        keyboard.add(our_contacts, FAQ, back)
        return keyboard

    def admin_btns(self):
        addproduct = types.InlineKeyboardButton('Добавить продукт', callback_data='addproduct')
        importproducts = types.InlineKeyboardButton('Обновить товары из excel', callback_data='importproducts')
        importcategories = types.InlineKeyboardButton('Обновить категории из excel', callback_data='importcategories')
        importsubcategories = types.InlineKeyboardButton('Обновить подкатегории из excel', callback_data='importsubcategories')
        changeproduct = types.InlineKeyboardButton('Изменить продукт', callback_data='changeproduct')
        changhecontact = types.InlineKeyboardButton('Изменить контакт', callback_data='changecontact')
        changefaq = types.InlineKeyboardButton('Изменить FAQ', callback_data='changefaq')
        changestartmsg = types.InlineKeyboardButton('Изменить стартовое сообщение', callback_data='changestartmsg')
        changesale = types.InlineKeyboardButton('Изменить скидку', callback_data='changesale')
        changecat = types.InlineKeyboardButton('Изменить текст категории', callback_data='changecat')
        changeprecat = types.InlineKeyboardButton('Изменить текст подкатегории', callback_data='changeprecat')
        changeprod = types.InlineKeyboardButton('Изменить текст товара', callback_data='changeprod')
        delete_product = types.InlineKeyboardButton('Удалить', callback_data='delete_product')
        self.__markup.add(addproduct, importproducts, importcategories, importsubcategories, changeproduct,
                          changhecontact, changefaq, changestartmsg, changesale, changecat, changeprecat, changeprod, delete_product)
        return self.__markup

    def categories_btns(self, data):
        data.append(('<main>', 'В главное меню'))
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            btn = types.InlineKeyboardButton(i[1], callback_data=f'categories{i[0]}')
            markup.add(btn)
        return markup

    def delete_btns(self):
        markup = types.InlineKeyboardMarkup(row_width=1)
        as1 = types.InlineKeyboardButton('Удалить категорию', callback_data='delete_cat')
        as2 = types.InlineKeyboardButton('Удалить подкатегорию', callback_data='delete_precat')
        as3 = types.InlineKeyboardButton('Удалить товар', callback_data='delete_prod')
        markup.add(as1, as2, as3)
        return markup

    def subcategories_btns(self, data):
        data.append(('<back>', 'назад'))
        data.append(('<main>', 'В главное меню'))
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            btn = types.InlineKeyboardButton(i[1], callback_data=f'subcategories{i[0]}')
            markup.add(btn)
        return markup

    def reference_btns(self):
        data = list()
        data.extend([('1', 'Да'), ('0', 'Нет'), ('<back>', 'назад'), ('<main>', 'В главное меню')])
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            btn = types.InlineKeyboardButton(i[1], callback_data=f'reference{i[0]}')
            markup.add(btn)
        return markup

    def products_btns(self, data):
        data.append(('<back>', 'назад'))
        data.append(('<main>', 'В главное меню'))
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            if i[0] not in ['<back>', '<main>']:
                btn = types.InlineKeyboardButton(f'{i[1]} * {i[2]}₽', callback_data=f'products{i[0]}')
            else:
                btn = types.InlineKeyboardButton(i[1], callback_data=f'products{i[0]}')
            markup.add(btn)
        return markup

    def buy_btns(self, id_product, instuction_url, distro_url):
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton('Купить', callback_data=f'buy{id_product}')
        btn2 = types.InlineKeyboardButton('Скачать дистрибутив', url=distro_url)
        btn3 = types.InlineKeyboardButton('Инструкция по активации', url=instuction_url)
        btn4 = types.InlineKeyboardButton('Назад', callback_data=f'buy<back>')
        btn5 = types.InlineKeyboardButton('В главное меню', callback_data=f'buy<main>')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        return markup

    def change_btns(self):
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton('Цену', callback_data=f'сhangecart1')
        btn2 = types.InlineKeyboardButton('Фото', callback_data=f'сhangecart2')
        btn3 = types.InlineKeyboardButton('Ключ', callback_data=f'сhangecart3')
        btn4 = types.InlineKeyboardButton('Подкатегорию', callback_data=f'сhangecart4')
        btn5 = types.InlineKeyboardButton('Описание', callback_data=f'сhangecart5')
        btn6 = types.InlineKeyboardButton('Превью', callback_data=f'сhangecart6')
        btn7 = types.InlineKeyboardButton('Инструкцию по активации', callback_data=f'сhangecart7')
        btn8 = types.InlineKeyboardButton('Ссылку на дистрибутив', callback_data=f'сhangecart8')
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8)
        return markup

    def purchased_btns(self, data):
        data.append(('<main>', 'В главное меню'))
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i in data:
            btn = types.InlineKeyboardButton(i[1], callback_data=f'purchased{i[0]}')
            markup.add(btn)
        return markup

    def pay_btn(self, price, url):
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton(f'Оплатить {price}₽', url=url)
        markup.add(btn)
        return markup

