#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image
import io
import time
from datetime import datetime
#####################################


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, [None, None, None, None]]}) # 1 - status, 2 - m
        return self.__user_data


class ExcellImport:
    def __init__(self, db):
        super(ExcellImport, self).__init__()
        self.__db = db
        self.__sheet = None
        self.init()
        self.excell()

    def init(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name('creditionals.json')
        gc = gspread.authorize(creds)
        self.__sheet = gc.open("Бот для продаж")

    def excell(self):
        worksheet = self.__sheet.get_worksheet(1) # 1 - вторая страница для парсинга
        data = worksheet.get_all_values()
        cell = self.__sheet.cell(2, 2).value  # Пример: ячейка B2
        img = Image.open(io.BytesIO(cell))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        photo = img_bytes.getvalue()
        print(data)


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
        self.__db.db_write('INSERT INTO products (photo, price, key, description) VALUES (?, ?, ?, ?)', data)

    def update_db_from_excell(self):
        pass

