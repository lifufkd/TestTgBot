#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from datetime import datetime
from PIL import Image
#####################################


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, [None, None, None, None, None], None]}) # 1 - status, 2 - m
        return self.__user_data


class ExcellImport:
    def __init__(self, db):
        super(ExcellImport, self).__init__()
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


class SheetExport:
    def __init__(self, db):
        super(SheetExport, self).__init__()
        self.__column_names_db = [['A1', 'B1', 'C1']]
        self.__db = db
        self.__sheet = None
        self.init()

    def init(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name('creditionals.json')
        file = gspread.authorize(creds)
        workbook = file.open("Бот для продаж")
        worksheet = self.__sheet.get_worksheet(0) # первая страница sheet
        self.__sheet = workbook.sheet1

    def update_excell(self):
        pass # тут инфа которую надо вставлять




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

    def add_one_product(self, data):
        self.__db.db_write(f'INSERT INTO products (photo, price, key, description, category, purchased) VALUES (?, ?, ?, ?, ?, {False})', data)

    def update_products_from_excell(self, data):
        check = self.__db.db_read(f'SELECT price, key, category, description FROM products', ())
        for i in data:
            try:
                i[1] = int(i[1])
                if tuple(i[1:]) not in check:
                    print(tuple(i[1:]), 'in')
                    self.__db.db_write(f'INSERT INTO products (photo, price, key, category, description, purchased) VALUES (?, ?, ?, ?, ?, ?)', (open('no-photo.png', 'rb'), int(i[1]), i[2], i[3], i[4], False))
            except:
                pass

    def update_categories_from_excell(self, data):
        check = self.__db.db_read(f'SELECT id, name FROM categories', ())
        for i in data:
            if tuple(i) not in check:
                self.__db.db_write(f'INSERT INTO categories (id, name) VALUES (?, ?)', i)

    def update_subcategories_from_excell(self, data):
        check = self.__db.db_read(f'SELECT id, id_categories, name FROM subcategories', ())
        for i in data:
            if tuple(i) not in check:
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

    def get_products_by_id(self, id_product):
        data = self.__db.db_read('SELECT row_id, photo, price, key, description FROM products WHERE category = ? AND purchased = 0', (id_product, ))
        return data

    def update_product(self, data, field, product_id):
        self.__db.db_write(f'UPDATE products SET {field} = ? WHERE row_id = ?', (data, product_id))

    def check_product_id_exist(self, product_id):
        data = self.__db.db_read('SELECT count(*) FROM products WHERE row_id = ?', (product_id,))
        if len(data) > 0:
            if data[0][0] > 0:
                status = True
            else:
                status = False
            return status


