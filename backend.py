#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import gspread
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
    def __init__(self, db, config):
        super(Excell, self).__init__()
        self.__db = db
        self.__config = config
        self.__sheet = None
        self.init()

    def init(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name('creditionals.json')
        gc = gspread.authorize(creds)
        self.__sheet = gc.open_by_key(self.__config.get_config()['google_table_id'])

    def config_excell(self):
        worksheet = self.__sheet.get_worksheet(0) # 1 - вторая страница для парсинга
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

    def update_config(self, data):
        index = list()
        for i in self.__db.db_read(f'SELECT row_id FROM tests', ()):
            index.append(str(i[0]))
        for i in data:
            if i[0] in index:
                self.__db.db_write(
                    f'UPDATE tests SET name = ?, description = ?, text_start_btn = ?, text_continue_btn = ?, before_test = ?, after_question = ?, after_test = ?, questions = ? WHERE row_id = {i[0]}',
                    (i[1], i[2], i[4], i[10], i[6], i[9], i[11], i[5]))
            else:
                self.__db.db_write(
                    f'INSERT INTO tests (row_id, name, description, text_start_btn, text_continue_btn, before_test, after_question, after_test, questions) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (i[0], i[1], i[2], i[4], i[10], i[6], i[9], i[11], i[5]))





    def add_one_product(self, datas):
        data = self.__db.db_read('SELECT MAX(row_id) FROM products', ())
        if len(data) > 0:
            new_id = int(data[0][0]) + 1
        else:
            new_id = 1
        self.__db.db_write(f'INSERT INTO products (row_id, photo, price, key, description, category, preview, distro_url, instruction_url) VALUES ({new_id}, ?, ?, ?, ?, ?, ?, ?, ?)', datas)

    def update_products_from_excell(self, data):
        index = list()
        for i in self.__db.db_read(f'SELECT row_id FROM products', ()):
            index.append(i[0])
        for i in data:
            try:
                if i[0] in index:
                    self.__db.db_write(f'UPDATE products SET price = ?, key = ?, preview = ?, category = ?, description = ?, distro_url = ?, instruction_url = ? WHERE row_id = {i[0]}', (i[1], i[2], i[3], i[4], i[5], i[6], i[7]))
                else:
                    self.__db.db_write(
                        f'INSERT INTO products (photo, row_id, price, key, preview, category, description, distro_url, instruction_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (open('no-photo.png', 'rb').read(), i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]))
            except:
                pass

    def update_categories_from_excell(self, data):
        index = list()
        for i in self.__db.db_read(f'SELECT id FROM categories', ()):
            index.append(i[0])
        for i in data:
            if i[0] in index:
                self.__db.db_write(f'UPDATE categories SET name = ? WHERE id = {i[0]}', (i[1], ))
            else:
                self.__db.db_write(f'INSERT INTO categories (id, name) VALUES (?, ?)', i)

    def get_preview_from_sales(self, user_id):
        products = self.__db.db_read('SELECT product, name FROM sales WHERE user_id = ? AND payment_status = ?', (user_id, True))
        return list(set(products))

    def delete_category(self, row_id):
        self.__db.db_write(f'DELETE FROM categories WHERE id = ?', (row_id, ))

    def update_subcategories_from_excell(self, data):
        index = list()
        for i in self.__db.db_read(f'SELECT id FROM subcategories', ()):
            index.append(i[0])
        for i in data:
            if i[0] in index:
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

    def delete_subcot(self, row_id):
        self.__db.db_write(f'DELETE FROM subcategories WHERE id = ?', (row_id, ))

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