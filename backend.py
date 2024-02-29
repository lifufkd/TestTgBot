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
            self.__user_data.update({user_id: [None]})
        return self.__user_data


class ExcellUpdate:
    def __init__(self, db):
        super(ExcellUpdate, self).__init__()
        self.__codes = {0: 'обращение в поддержку', 1: 'запрос на отзыв', 2: 'сообщение от пользователя', 3: 'сообщение от модератора'}
        self.__column_names_db = [['Дата время (UTC)', 'Пользователь (TG)', 'Тип запроса']]
        self.__column_names_quanity = [['Поддержка', 'Отзыв', 'Всего обращений', 'Ответ менеджера']]
        self.__db = db
        self.__sheet = None
        self.init()

    def init(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json')
        file = gspread.authorize(creds)
        workbook = file.open("события бота")
        self.__sheet = workbook.sheet1

    def update_excell(self):
        data = self.__column_names_db + self.get_db_data()
        self.__sheet.update(f'A1:C{len(data)}', data)
        data1 = self.__column_names_quanity + [[self.get_quanity(0), self.get_quanity(1), self.get_quanity(2), self.get_quanity(3)]]
        self.__sheet.update(f'F1:I{len(data1)}', data1)

    def get_db_data(self):
        formated = []
        data = self.__db.db_read("SELECT time, nick_tg, request_type FROM actions", ())
        if len(data) > 0:
            for row in data:
                formated.append([datetime.utcfromtimestamp(row[0]).strftime('%Y-%m-%d %H:%M:%S'), row[1], self.__codes[row[2]]])
        return formated

    def get_quanity(self, req_type):
        data = self.__db.db_read('SELECT count(*) FROM actions WHERE request_type = ?', (req_type, ))
        if len(data) > 0:
            return data[0][0]


class DbAct:
    def __init__(self, db, config):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config
        self.__excell_update = ExcellUpdate(db)
        #self.__excell_update.update_excell()

    def add_user(self, user_id, first_name, last_name, nick_name):
        if not self.user_is_existed(user_id):
            if user_id in self.__config.get_config()['admins']:
                is_admin = True
            else:
                is_admin = False
            self.__db.db_write('INSERT INTO users (user_id, first_name, last_name, nick_name, is_admin) VALUES (?, ?, ?, ?, ?)', (user_id, first_name, last_name, nick_name, is_admin))

