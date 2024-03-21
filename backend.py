#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import json
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
            self.__user_data.update({user_id: [None, [], None, None, None]}) # 1 - status, 2 - m
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

    def update_questions(self):
        index = list()
        for i in self.__db.db_read(f'SELECT row_id, id_test FROM questions', ()):
            index.append(i)
        quanity, names = self.__sheet.get_names_lists()
        for g in range(quanity):
            data = self.__sheet.questions_excell(g+2)
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

    def get_all_tests(self):
        data = self.__db.db_read('SELECT row_id, name FROM tests', ())
        return data

    def pre_test_data(self, test_id):
        data = self.__db.db_read('SELECT name, before_test, description, text_start_btn, questions FROM tests WHERE row_id = ?', (test_id, ))
        if len(data) > 0:
            data = data[0]
            quanity = self.__db.db_read('SELECT COUNT(*) FROM questions WHERE id_test = ?', (data[4],))[0][0]
            return quanity, data[:4]
        else:
            return None, None

    def get_question(self, quest_id):
        quanity = self.__db.db_read('SELECT name, questions FROM questions WHERE row_id = ?', (quest_id, ))[0]
        quests = json.loads(quanity[1])
        return quanity[0], quests

    def get_after_quest(self, id_test, id_quest):
        test = self.__db.db_read('SELECT after_question, text_continue_btn FROM tests WHERE row_id = ?', (id_test,))[0]
        quest = self.__db.db_read('SELECT answer_description FROM questions WHERE row_id = ?', (id_quest,))[0][0]
        return test, quest

    def get_questions_id_by_test_id(self, test_id):
        return self.__db.db_read('SELECT questions FROM tests WHERE row_id = ?', (test_id,))[0][0]

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

    def check_correct(self, question_id, index):
        correct = self.__db.db_read('SELECT correct FROM questions WHERE row_id = ?', (question_id,))[0][0]
        if index == str(correct):
            return True

    def get_marks_by_stat(self, test_name, user_nick):
        data = self.__db.db_read('SELECT marks FROM statistic WHERE test_name = ? AND user_nick = ?', (test_name, user_nick))
        print(test_name)
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