#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
#####################################


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, [], None, None, None, [], [], False, 0]}) # 1 - status, 2 - m
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

    def get_names_lists(self):
        worksheet = self.__sheet.worksheets()
        number_of_sheets = len(worksheet)
        return number_of_sheets - 2, worksheet

    def download_file_from_google_drive(self, id):
        URL = "https://docs.google.com/uc?export=download"
        out = b''
        session = requests.Session()
        response = session.get(URL, params={'id': id}, stream=True)
        token = self.get_confirm_token(response)
        if token:
            params = {'id': id, 'confirm': token}
            response = session.get(URL, params=params, stream=True)
        for chunk in response.iter_content(32768):
            if chunk:
                out += chunk
        if out[:5] == b'<html':
            out = b''
        return out

    def get_confirm_token(self, response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    def questions_excell(self, index):
        worksheet = self.__sheet.get_worksheet(index) # 1 - третья страница для парсинга
        data = worksheet.get_all_values()[1:]
        return data

    def get_statistic_excell(self):
        worksheet = self.__sheet.get_worksheet(1) # 1 - четвертая страница для парсинга
        data = worksheet.get_all_values()
        return data[1:]

    def update_statistic_excell(self, data, index):
        worksheet = self.__sheet.get_worksheet(1)  # 1 - четвертая страница для парсинга
        cell_list = worksheet.range(f'A{index}:F{index}')
        for i in range(len(cell_list)):
            cell_list[i].value = data[i]
        worksheet.update_cells(cell_list)

    def add_stat(self, values):
        worksheet = self.__sheet.get_worksheet(1)
        lastRow = len(worksheet.get_all_values()) + 1
        cell_list = worksheet.range(f'A{lastRow}:F{lastRow}')
        for i in range(len(cell_list)):
            cell_list[i].value = values[i]
        worksheet.update_cells(cell_list)


class DbAct:
    def __init__(self, db, config, sheet):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config
        self.__sheet = sheet

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
        data_index = list()
        for i in self.__db.db_read(f'SELECT row_id FROM tests', ()):
            index.append(str(i[0]))
        for i in data:
            data_index.append(i[0])
        for i in data:
            correct_link = self.__sheet.download_file_from_google_drive(i[7][32:65])
            incorrect_link = self.__sheet.download_file_from_google_drive(i[8][32:65])
            if i[0] in index:
                self.__db.db_write(
                    f'UPDATE tests SET name = ?, description = ?, text_start_btn = ?, text_continue_btn = ?, '
                    f'before_test = ?, after_question_c = ?, after_test = ?, after_question_i = ?, correct_link = ?, '
                    f'incorrect_link = ?, questions = ?, test_command = ?, row_width = ?, start_question = ?, start_answer = ?, '
                    f'again_test_btn = ?, new_test_btn = ? WHERE row_id = {i[0]}',
                    (i[1], i[2], i[4], i[11], i[6], i[9], i[12], i[10], correct_link, incorrect_link, i[5], i[3], i[13], i[14], i[15], i[16], i[17]))
            else:
                self.__db.db_write(
                    f'INSERT INTO tests (row_id, name, description, text_start_btn, text_continue_btn, before_test, '
                    f'after_question_c, after_test, after_question_i, correct_link, incorrect_link, questions, test_command, '
                    f'row_width, start_question, start_answer, again_test_btn, new_test_btn) '
                    f'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (i[0], i[1], i[2], i[4], i[11], i[6], i[9], i[12], i[10], correct_link, incorrect_link, i[5], i[3], i[13], i[14], i[15], i[16], i[17]))
        for i in index:
            if i not in data_index:
                self.__db.db_write(f'DELETE FROM tests WHERE row_id = ?', (i, ))

    def update_questions(self):
        index = list()
        data_index = list()
        for i in self.__db.db_read(f'SELECT row_id, id_test FROM questions', ()):
            index.append(i)
        quanity, names = self.__sheet.get_names_lists()
        for g in range(quanity):
            data = self.__sheet.questions_excell(g+2)
            for i in data:
                data_index.append((i[0], names[g+2].title))
            for i in data:
                enc_answers = json.dumps(i[4:])
                if (i[0], names[g+2].title) in index:
                    self.__db.db_write(
                        f'UPDATE questions SET name = ?, questions = ?, answer_description = ?, correct = ?, id_test = ? WHERE row_id = {i[0]} AND id_test = "{names[g+2].title}"',
                        (i[1], enc_answers, i[2], i[3], names[g+2].title))
                else:
                    self.__db.db_write(
                        f'INSERT INTO questions (row_id, name, questions, answer_description, correct, id_test) VALUES (?, ?, ?, ?, ?, ?)',
                        (i[0], i[1], enc_answers, i[2], i[3], names[g+2].title))
        for i in index:
            if i not in data_index:
                print(i)
                print(data_index)
                self.__db.db_write(f'DELETE FROM questions WHERE row_id = ? AND id_test = ?', i)

    def get_all_tests(self):
        data = self.__db.db_read('SELECT row_id, name FROM tests', ())
        return data

    def get_start_question(self, id_test):
        return self.__db.db_read('SELECT start_question FROM tests WHERE row_id = ?',
                                    (id_test, ))[0][0]



    def pre_test_data(self, test_id):
        data = self.__db.db_read('SELECT name, before_test, description, text_start_btn, questions FROM tests WHERE row_id = ?', (test_id, ))
        if len(data) > 0:
            data = data[0]
            quanity = self.__db.db_read('SELECT COUNT(*) FROM questions WHERE id_test = ?', (data[4],))[0][0]
            return quanity, data[:4]
        else:
            return None, None

    def command_run(self, test_command):
        data = self.__db.db_read('SELECT name, before_test, description, text_start_btn, row_id, questions FROM tests WHERE test_command = ?', (test_command, ))
        if len(data) > 0:
            data = data[0]
            quanity = self.__db.db_read('SELECT COUNT(*) FROM questions WHERE id_test = ?', (data[5],))[0][0]
            return quanity, data[:5]
        else:
            return None, None

    def get_question(self, quest_id, id_test):
        quanity = self.__db.db_read('SELECT name, questions FROM questions WHERE row_id = ? AND id_test = ?', (quest_id, id_test))[0]
        row_width = self.__db.db_read('SELECT row_width FROM tests WHERE questions = ?',
                                    (id_test, ))[0][0]
        quanity = list(quanity)
        quanity.insert(1, row_width)
        quests = json.loads(quanity[2])
        return quanity[:2], quests

    def get_after_quest(self, id_test, id_quest):
        test = self.__db.db_read('SELECT after_question_c, after_question_i, text_continue_btn, correct_link, incorrect_link, start_answer, questions FROM tests WHERE row_id = ?', (id_test,))[0]
        quest = self.__db.db_read('SELECT answer_description FROM questions WHERE row_id = ? AND id_test = ?', (id_quest, test[6]))[0][0]
        return test[:6], quest

    def get_questions_id_by_test_id(self, test_id):
        return self.__db.db_read('SELECT questions FROM tests WHERE row_id = ?', (test_id,))[0][0]

    def get_questions_end_btn(self, test_id):
        return self.__db.db_read('SELECT new_test_btn, again_test_btn FROM tests WHERE row_id = ?', (test_id,))[0]

    def get_test_name_by_id(self, test_id):
        data = self.__db.db_read('SELECT name FROM tests WHERE row_id = ?', (test_id, ))[0][0]
        return data

    def get_id_quest_by_master(self, id_test):
        out = list()
        pr = self.get_questions_id_by_test_id(id_test)
        quanity = self.__db.db_read('SELECT row_id FROM questions WHERE id_test = ?', (pr,))
        for i in quanity:
            out.append(i[0])
        return out

    def check_correct(self, question_id, index, trd):
        id_test = self.get_questions_id_by_test_id(trd)
        correct = self.__db.db_read('SELECT correct FROM questions WHERE row_id = ? AND id_test = ?', (question_id, id_test))[0][0]
        if index == str(correct):
            return True

    def get_marks_by_stat(self, test_name, user_nick):
        data = self.__db.db_read('SELECT marks FROM statistic WHERE test_name = ? AND user_nick = ?', (test_name, user_nick))
        if len(data) > 0:
            return data[0][0]
        else:
            return 0

    def get_test_name_by_ids(self, id):
        return self.__db.db_read('SELECT name FROM tests WHERE row_id = ?',
                                 (id, ))[0][0]


    def add_entry_statistic(self, datas, test_name, user_nick):
        data = self.__db.db_read('SELECT COUNT(*) FROM statistic WHERE test_name = ? AND user_nick = ?', (test_name, user_nick))[0][0]
        if data == 0:
            self.__db.db_write(
                f'INSERT INTO statistic (date, progress, marks, test_name, user_nick) VALUES (?, ?, ?, ?, ?)',
                (datas[0], datas[1], datas[2], test_name, user_nick))
            row = self.__db.db_read('SELECT MAX(row_id) FROM statistic', ())[0][0]
        else:
            self.__db.db_write(
                f'UPDATE statistic SET date = ?, progress = ?, marks = ? WHERE test_name = "{test_name}" AND user_nick = "{user_nick}"',
                (datas[0], datas[1], datas[2]))
            row = self.__db.db_read('SELECT row_id FROM statistic WHERE test_name = ? AND user_nick = ?', (test_name, user_nick))[0][0]
        return row

    def add_entry_statistic_excel(self, datas, test_name, user_nick, row):
        index = list()
        data = self.__sheet.get_statistic_excell()
        for i in data:
            index.append(i[0])
        check = self.__db.db_read('SELECT row_id FROM statistic WHERE test_name = ? AND user_nick = ?',
                                 (test_name, user_nick))[0][0]
        if str(check) in index:
            self.__sheet.update_statistic_excell([row, datas[0], test_name, user_nick, datas[1], datas[2]], index.index(str(check))+2)
        else:
            self.__sheet.add_stat([row, datas[0], test_name, user_nick, datas[1], datas[2]])

    def get_requiem(self, test_id):
        return self.__db.db_read('SELECT after_test FROM tests WHERE row_id = ?',
                                 (test_id, ))[0][0]