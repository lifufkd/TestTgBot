#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import platform
import telebot
from threading import Lock
from backend import TempUserData, DbAct, Excell
from config_parser import ConfigParser
from db import DB
from datetime import datetime
import pytz
from frontend import Bot_inline_btns
####################################################################
config_name = 'secrets.json'
####################################################################


def get_tests():
    s = ''
    data = db_actions.get_all_tests()
    for i in data:
        s += f'{i[0]}. {i[1]}\n'
    return s


def get_question(test_id):
    s = ''
    name, questions = db_actions.get_question(test_id)
    s += f'Вопрос: {name}\n'
    for i in range(len(questions)):
        s += f'{i+1}. {questions[i]}\n'
    return s

def get_category():
    s = ''
    data = db_actions.get_categories()
    for i in data:
        s += f'{i[0]}. {i[1]}\n'
    return s


def main():
    @bot.message_handler(commands=['start'])
    def start_message(message):
        user_id = message.chat.id
        db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                            f'@{message.from_user.username}')
        buttons = Bot_inline_btns()
        bot.send_message(message.chat.id,
                         f'Привет {message.from_user.first_name}👋\n'
                         'Я помогу вам найти тест!',
                         reply_markup=buttons.start_buttons())

    @bot.message_handler(commands=['admin'])
    def tovar_msg(message):
        command = message.text.replace('/', '')
        user_id = message.chat.id
        if db_actions.user_is_existed(user_id):
            buttons = Bot_inline_btns()
            if db_actions.user_is_admin(user_id):
                if command == 'admin':
                    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}!\n',
                                     reply_markup=buttons.admin_btns())
        else:
            bot.send_message(message.chat.id, 'Введите /start для запуска бота')

    @bot.message_handler(content_types=['text', 'photo'])
    def text_message(message):
        photo = message.photo
        tg_nick = message.chat.username
        user_input = message.text
        user_id = message.chat.id
        if db_actions.user_is_existed(user_id):
            buttons = Bot_inline_btns()
            if temp_user_data.temp_data(user_id)[user_id][0] is not None:
                status = temp_user_data.temp_data(user_id)[user_id][0]
                if status == 0:
                    quanity, data = db_actions.pre_test_data(user_input)
                    if quanity and data is not None:
                        temp_user_data.temp_data(user_id)[user_id][0] = None
                        bot.send_message(user_id, f'Название теста: {data[0]}\nКоличество вопросов: {quanity}\nОписание:\n{data[2]}\nПримечания:\n{data[1]}', reply_markup=buttons.start_test_btn(data[3], user_input))
                    else:
                        bot.send_message(user_id, 'Тест не существует')
                if status == 1:
                    all_questions = len(temp_user_data.temp_data(user_id)[user_id][1])
                    if all_questions - temp_user_data.temp_data(user_id)[user_id][2] >= 0 and temp_user_data.temp_data(user_id)[user_id][4]:
                        temp_user_data.temp_data(user_id)[user_id][2] += 1
                        index = temp_user_data.temp_data(user_id)[user_id][2] - 1
                        test_name = db_actions.get_test_name_by_id(temp_user_data.temp_data(user_id)[user_id][3])
                        marks = db_actions.get_marks_by_stat(test_name, f'@{tg_nick}')
                        progress = round(100*temp_user_data.temp_data(user_id)[user_id][2]/all_questions, 0)
                        current_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%d-%m-%Y')
                        after_quest, solve = db_actions.get_after_quest(temp_user_data.temp_data(user_id)[user_id][3], temp_user_data.temp_data(user_id)[user_id][1][index])
                        if index == 0:
                            marks = 0
                        temp_user_data.temp_data(user_id)[user_id][4] = False
                        if db_actions.check_correct(temp_user_data.temp_data(user_id)[user_id][1][index], user_input):
                            row = db_actions.add_entry_statistic([current_time, progress, marks+1], test_name, f'@{tg_nick}')
                            db_actions.add_entry_statistic_excel([current_time, progress, marks+1], test_name, f'@{tg_nick}', row)
                            pre_text = after_quest[0].replace('{баллов}', f'{str(marks+1)} баллов')
                            if all_questions != index+1:
                                bot.send_message(user_id, f'{pre_text}\nВы ответили правильно!', reply_markup=buttons.contiue_test_btn(after_quest[1], temp_user_data.temp_data(user_id)[user_id][1][index+1]))
                            else:
                                bot.send_message(user_id, f'{pre_text}\nВы ответили правильно!',
                                                 reply_markup=buttons.end_test_btn(temp_user_data.temp_data(user_id)[user_id][3]))
                        else:
                            row = db_actions.add_entry_statistic([current_time, progress, marks], test_name, f'@{tg_nick}')
                            db_actions.add_entry_statistic_excel([current_time, progress, marks], test_name,
                                                                 f'@{tg_nick}', row)
                            pre_text = after_quest[0].replace('{баллов}', f'{str(marks)} баллов')
                            if all_questions != index + 1:
                                bot.send_message(user_id, f'{pre_text}\n{solve}\nВы ответили неправильно',
                                                 reply_markup=buttons.contiue_test_btn(after_quest[1], temp_user_data.temp_data(user_id)[user_id][1][index+1]))
                            else:
                                bot.send_message(user_id, f'{pre_text}\nВы ответили неправильно',
                                                 reply_markup=buttons.end_test_btn(temp_user_data.temp_data(user_id)[user_id][3]))
            else:
                if message.text == '🗂 Посмотреть доступные тесты':
                    temp_user_data.temp_data(user_id)[user_id][0] = 0
                    bot.send_message(user_id, f'Выберите тест введя его номер:\n{get_tests()}')
        else:
            bot.send_message(message.chat.id, 'Введите /start для запуска бота')

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        command = call.data
        tg_nick = call.message.chat.username
        message_id = call.message.id
        user_id = call.message.chat.id
        if db_actions.user_is_existed(user_id):
            buttons = Bot_inline_btns()
            if db_actions.user_is_admin(user_id):
                if command == 'sync':
                    db_actions.update_config(sheet.config_excell())
                    db_actions.update_questions()
                    bot.send_message(user_id, 'Обновление успешно завершено!')
            if command[:10] == 'start_test':
                if temp_user_data.temp_data(user_id)[user_id][0] is None:
                    temp_user_data.temp_data(user_id)[user_id][1] = db_actions.get_id_quest_by_master(command[10:]) # id вопросов [0, 1, 2]
                    temp_user_data.temp_data(user_id)[user_id][0] = 1
                    temp_user_data.temp_data(user_id)[user_id][2] = 0 #пройденных вопросов
                    temp_user_data.temp_data(user_id)[user_id][3] = command[10:]
                    temp_user_data.temp_data(user_id)[user_id][4] = True
                    bot.send_message(user_id, get_question(temp_user_data.temp_data(user_id)[user_id][1][0]))
            elif command[:8] == 'continue':
                if command[8:] in temp_user_data.temp_data(user_id)[user_id][1] and temp_user_data.temp_data(user_id)[user_id][0] is not None:
                    temp_user_data.temp_data(user_id)[user_id][4] = True
                    bot.send_message(user_id, get_question(command[8:]))
            elif command[:3] == 'end':
                if temp_user_data.temp_data(user_id)[user_id][0] is not None:
                    data = db_actions.get_requiem(command[3:])
                    data = data.replace('#{баллов}', str(db_actions.get_marks_by_stat(db_actions.get_test_name_by_ids(command[3:]), f'@{tg_nick}')))
                    data = data.replace('#{вопросов_всего}', str(len(temp_user_data.temp_data(user_id)[user_id][1])))
                    temp_user_data.temp_data(user_id)[user_id][0] = None
                    bot.send_message(user_id, data)

        else:
            bot.send_message(user_id, 'Введите /start для запуска бота')

    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    config = ConfigParser(config_name, os_type)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    sheet = Excell(db, config)
    db_actions = DbAct(db, config, sheet)
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
