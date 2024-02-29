#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from datetime import datetime
#####################################


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, None]}) # 1 - status, 2 - m
        return self.__user_data


class ExcellImport:
    def __init__(self, db):
        super(ExcellImport, self).__init__()
        self.__codes = {0: 'обращение в поддержку', 1: 'запрос на отзыв', 2: 'сообщение от пользователя', 3: 'сообщение от модератора'}
        self.__column_names_db = [['Дата время (UTC)', 'Пользователь (TG)', 'Тип запроса']]
        self.__column_names_quanity = [['Поддержка', 'Отзыв', 'Всего обращений', 'Ответ менеджера']]
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
        print(data)

        # gc = gspread.service_account(filename='path/to/credentials.json')
        # worksheet = gc.open('Название таблицы').sheet1



class DbAct:
    def __init__(self, db, config):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config
        #self.__excell_update = ExcellUpdate(db)
        #self.__excell_update.update_excell()

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

