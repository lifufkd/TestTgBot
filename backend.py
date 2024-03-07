#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import time

import gspread
import hashlib
import requests
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
#####################################


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, [None, None, None, None, None, None, None, None], None, None, None, None, None, None]}) # 1 - status, 2 - m
        return self.__user_data


class Excell:
    def __init__(self, db):
        super(Excell, self).__init__()
        self.__db = db
        self.__sheet = None
        self.init()

    def init(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name('creditionals.json')
        gc = gspread.authorize(creds)
        self.__sheet = gc.open("Бот для продаж")

    def products_excell(self):
        worksheet = self.__sheet.get_worksheet(1) # 1 - вторая страница для парсинга
        data = worksheet.get_all_values()
        return data[1:]

    def categories_excell(self):
        worksheet = self.__sheet.get_worksheet(2) # 1 - третья страница для парсинга
        data = worksheet.get_all_values()
        return data[1:]

    def subcategories_excell(self):
        worksheet = self.__sheet.get_worksheet(3) # 1 - четвертая страница для парсинга
        data = worksheet.get_all_values()
        return data[1:]

    def add_sale(self, values):
        worksheet = self.__sheet.get_worksheet(0)
        lastRow = len(worksheet.get_all_values()) + 1
        cell_list = worksheet.range(f'A{lastRow}:F{lastRow}')
        for i in range(len(cell_list)):
            cell_list[i].value = values[i]
        worksheet.update_cells(cell_list)

class DbAct:
    def __init__(self, db, config):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config

    def add_user(self, user_id, first_name, last_name, nick_name):
        if not self.user_is_existed(user_id):
            if user_id in self.__config.get_config()['admins']:
                is_admin = True
            else:
                is_admin = False
            self.__db.db_write('INSERT INTO users (user_id, first_name, last_name, nick_name, is_admin) VALUES (?, ?, ?, ?, ?)', (user_id, first_name, last_name, nick_name, is_admin))

    def user_is_existed(self, user_id):
        data = self.__db.db_read('SELECT count(*) FROM users WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            if data[0][0] > 0:
                status = True
            else:
                status = False
            return status

    def user_is_admin(self, user_id):
        data = self.__db.db_read('SELECT is_admin FROM users WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            if data[0][0] == 1:
                status = True
            else:
                status = False
            return status

    def get_sale_by_id(self, sale_id):
        s = ''
        data = self.__db.db_read(f'SELECT time, key, price FROM sales WHERE product = ? AND payment_status = ?', (sale_id, True))
        for i in data:
            s += f"Время покупки: {datetime.utcfromtimestamp(i[0]).strftime('%d.%m.%Y %H:%M:%S')}\nКлюч: {i[1]}\nСумма покупки: {i[2]} ₽\n\n"
        return s

    def add_one_product(self, datas):
        data = self.__db.db_read('SELECT MAX(row_id) FROM products', ())
        if len(data) > 0:
            new_id = int(data[0][0]) + 1
        else:
            new_id = 1
        self.__db.db_write(f'INSERT INTO products (row_id, photo, price, key, description, category, preview, distro_url, instruction_url) VALUES ({new_id}, ?, ?, ?, ?, ?, ?, ?, ?)', datas)

    def update_products_from_excell(self, data):
        check = self.__db.db_read(f'SELECT row_id FROM products', ())
        for i in data:
            try:
                i[1] = int(i[1])
                if tuple(i[0]) in check:
                    old_key = self.__db.db_read(f'SELECT key FROM products WHERE row_id = ?', (i[0], ))[0][0]
                    new_keys = ','.join(set(old_key.split(',') + i[2].split(',')))
                    self.__db.db_write(f'UPDATE products SET price = ?, key = ?, preview = ?, category = ?, description = ?, distro_url = ?, instruction_url = ? WHERE row_id = {i[0]}', (i[1], new_keys, i[3], i[4], i[5], i[6], i[7]))
                else:
                    self.__db.db_write(
                        f'INSERT INTO products (photo, row_id, price, key, preview, category, description, distro_url, instruction_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (open('no-photo.png', 'rb').read(), i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]))
            except:
                pass


    def update_categories_from_excell(self, data):
        check = self.__db.db_read(f'SELECT id FROM categories', ())
        for i in data:
            if tuple(i[0]) in check:
                self.__db.db_write(f'UPDATE categories SET name = ? WHERE id = {i[0]}', (i[1], ))
            else:
                self.__db.db_write(f'INSERT INTO categories (id, name) VALUES (?, ?)', i)

    def get_preview_from_sales(self, user_id):
        products = self.__db.db_read('SELECT product, name FROM sales WHERE user_id = ? AND payment_status = ?', (user_id, True))
        return list(set(products))

    def update_subcategories_from_excell(self, data):
        check = self.__db.db_read(f'SELECT id FROM subcategories', ())
        for i in data:
            if tuple(i[0]) in check:
                self.__db.db_write(f'UPDATE subcategories SET id_categories = ?, name = ? WHERE id = {i[0]}', (i[1], i[2]))
            else:
                self.__db.db_write(f'INSERT INTO subcategories (id, id_categories, name) VALUES (?, ?, ?)', i)

    def get_categories(self):
        data = self.__db.db_read('SELECT id, name FROM categories', ())
        return data

    def get_sub_by_id_categories(self, id_categories):
        data = self.__db.db_read('SELECT id, name FROM subcategories WHERE id_categories = ?', (id_categories, ))
        return data

    def get_subcategories(self):
        data = self.__db.db_read('SELECT id, name FROM subcategories', ())
        return data

    def get_product_by_id(self, id_product):
        data = self.__db.db_read('SELECT photo, price, description, instruction_url, distro_url FROM products WHERE row_id = ?', (id_product, ))
        return data[0]

    def get_products_preview(self, id_product):
        data = self.__db.db_read(
            'SELECT row_id, preview, price FROM products WHERE category = ?',
            (id_product, ))
        return data

    def get_all_products_preview(self):
        data = self.__db.db_read(
            'SELECT row_id, preview, price FROM products',
            ())
        return data

    def delete_product(self, product_id):
        self.__db.db_write(f'DELETE FROM products WHERE row_id = ?', (product_id, ))

    def update_product(self, data, field, product_id):
        self.__db.db_write(f'UPDATE products SET {field} = ? WHERE row_id = ?', (data, product_id))

    def add_sale(self, data):
        self.__db.db_write(f'INSERT INTO sales (time, name, price, payment_status, nick_tg, user_id, key, product) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', data)
        return self.__db.db_read(f'SELECT max(row_id) FROM sales', ())[0][0]

    def update_sale(self, time, payment_status, product_id):
        self.__db.db_write(f'UPDATE sales SET time = ?, payment_status = ? WHERE row_id = ?', (time, payment_status, product_id))

    def get_product_by_id_for_buy(self, id_product):
        out = list()
        data = self.__db.db_read('SELECT price, key, description, category, preview FROM products WHERE row_id = ?', (id_product,))[0]
        sub_cat_data = self.__db.db_read('SELECT id_categories, name FROM subcategories WHERE id = ?', (data[3],))[0]
        cat_data = self.__db.db_read('SELECT name FROM categories WHERE id = ?', (sub_cat_data[0],))[0]
        out.append(f'{cat_data[0]} - {sub_cat_data[1]} - {data[4]}')
        out.extend(data[0:3])
        return out

    def get_all_keys_product(self, product_id):
        data = self.__db.db_read(
            'SELECT key FROM products WHERE row_id = ?',
            (product_id, ))
        if len(data) > 0:
            return data[0][0]


    def check_product_id_exist(self, product_id):
        data = self.__db.db_read('SELECT count(*) FROM products WHERE row_id = ?', (product_id,))
        if len(data) > 0:
            if data[0][0] > 0:
                status = True
            else:
                status = False
            return status

    def check_already_open_sale(self, user_id):
        return self.__db.db_read(f'SELECT count(*) FROM sales WHERE user_id = ? AND time = ?', (user_id, 0))[0][0]


class Payment:
    def __init__(self, config, db_act, sheet):
        super(Payment, self).__init__()
        self.__config = config
        self.__db_act = db_act
        self.__sheet = sheet

    def shedule(self, order_id, payment_id, name, price, user_id, msg_id, bot, key, product_id):
        c = 0
        keys = list()
        while True:
            status = self.check_payment(payment_id, order_id)
            c += 1
            if c >= self.__config.get_config()['payment_timeout'] * 60:
                timee = time.time()
                self.__db_act.update_sale(timee, False, order_id)
                self.__sheet.add_sale(
                    [datetime.utcfromtimestamp(timee).strftime('%d.%m.%Y %H:%M:%S'), name, price, 'Отклонена',
                     user_id, 'Нет'])
                product = self.__db_act.get_product_by_id_for_buy(product_id)
                for i in product[2].split(','):
                    if i != '':
                        keys.append(i)
                keys.append(key)
                self.__db_act.update_product(','.join(keys), 'key', product_id)
                bot.delete_message(user_id, msg_id)
                bot.send_message(user_id, "Время на оплату истекло, попробуйте ещё раз")
                break # end deny pay
            elif status in ['AUTH_FAIL', 'REJECTED']:
                timee = time.time()
                self.__db_act.update_sale(timee, False, order_id)
                self.__sheet.add_sale(
                    [datetime.utcfromtimestamp(timee).strftime('%d.%m.%Y %H:%M:%S'), name, price, 'Отклонена',
                     user_id, 'Нет'])
                product = self.__db_act.get_product_by_id_for_buy(product_id)
                for i in product[2].split(','):
                    if i != '':
                        keys.append(i)
                keys.append(key)
                self.__db_act.update_product(','.join(keys), 'key', product_id)
                bot.delete_message(user_id, msg_id)
                bot.send_message(user_id, "Оплата не успешна, попробуйте ещё раз")
            elif status in ['CONFIRMED', 'AUTHORIZED']:
                timee = time.time()
                self.__db_act.update_sale(timee, True, order_id)
                self.__sheet.add_sale(
                    [datetime.utcfromtimestamp(timee).strftime('%d.%m.%Y %H:%M:%S'), name, price, 'Успешна',
                     user_id, key])
                bot.delete_message(user_id, msg_id)
                bot.send_message(user_id,
                                 f'Оплата совершена успешно, полная информация о вашей покупке продублирована в '
                                 f'Профиль>Мои покупки\nВаш лицензионный ключ: {key}')
                break
            time.sleep(1)

    def get_sha_key(self):
        t = []
        r = {
            "TerminalKey": self.__config.get_config()['token'],
            "Amount": 1000,
            "OrderId": "1",
            "Password": self.__config.get_config()['terminal_password']
        }
        for key, value in r.items():
            t.append({key: value})
        t = sorted(t, key=lambda x: list(x.keys())[0])
        t = "".join(str(value) for item in t for value in item.values())
        sha256 = hashlib.sha256()
        sha256.update(t.encode('utf-8'))
        t = sha256.hexdigest()
        return t

    def create_new_payment(self, name, price, desc, order_id):
        api_url = "https://securepay.tinkoff.ru/v2/Init"
        payload = {
            "TerminalKey": self.__config.get_config()['token'],
            "Amount": price*100,
            "OrderId": order_id,
            "Description": desc,
            "Token": self.get_sha_key(),
            "DATA": {
                "Email": "ваша@почта.ru"},
            "Receipt": {
                "Email": "ваша@почта.ru",
                "Taxation": "osn",
                "Items": [
                    {
                        "Name": name,
                        "Price": 10000,
                        "Quantity": 1.00,
                        "Amount": price*100,
                        "Tax": "none"
                    },
                ]
            }
        }
        response = requests.post(api_url, json=payload).json()
        return [response['PaymentURL'], response['PaymentId']]

    def check_payment(self, payment_id, order_id):
        api_url = "https://securepay.tinkoff.ru/v2/GetState"
        tokentr = self.__config.get_config()['terminal_password'] + payment_id + self.__config.get_config()['token']
        tokensha256 = str(hashlib.sha256(tokentr.encode()).hexdigest())
        payload = {
            "TerminalKey": self.__config.get_config()['token'],
            "PaymentId": payment_id,
            "Token": tokensha256,
            "OrderId": order_id,
        }
        response = requests.post(api_url, json=payload).json()
        return response['Status']
