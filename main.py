#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import platform
import telebot
import threading
import re
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


def get_question(test_id, quest_id):
    s = ''
    name, questions = db_actions.get_question(test_id, quest_id)
    print(questions)
    s += f'Вопрос: {name}'
    return s, questions


def split_text(text):
    sentence_endings = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
    sentences = re.split(sentence_endings, text)
    result = []
    current_line = ''
    for sentence in sentences:
        if len(current_line) + len(sentence) <= 1000:
            current_line += sentence
        else:
            result.append(current_line)
            current_line = sentence
    if current_line:
        result.append(current_line)
    return result


def get_after_test(test_id, user_nick, user_id):
    data = db_actions.get_requiem(test_id)
    data = data.replace('#{баллов}',
                        str(db_actions.get_marks_by_stat(db_actions.get_test_name_by_ids(test_id),
                                                         f'https://t.me/{user_nick}')))
    data = data.replace('#{вопросов_всего}', str(len(temp_user_data.temp_data(user_id)[user_id][1])))
    return data

def main():
    @bot.message_handler(commands=['start'])
    def start_message(message):
        command = message.text.replace('/', '')
        user_id = message.chat.id
        db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                            f'@{message.from_user.username}')
        buttons = Bot_inline_btns()
        if command == 'start':
            bot.send_message(message.chat.id,
                             f'Привет {message.from_user.first_name}👋\n'
                             'Я помогу вам найти тест!',
                             reply_markup=buttons.start_buttons('Найти тест'))
        elif command[:5] == 'start':
            quanity, data = db_actions.command_run(command[6:])
            if quanity and data is not None:
                temp_user_data.temp_data(user_id)[user_id][0] = None
                bot.send_message(user_id, f'{data[1]}',
                                 reply_markup=buttons.start_test_btn(data[3], data[4]))
            else:
                bot.send_message(user_id, 'Тест не существует')

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
                        bot.send_message(user_id, f'{data[1]}',
                                         reply_markup=buttons.start_test_btn(data[3], user_input))
                    else:
                        bot.send_message(user_id, 'Тест не существует')
        else:
            bot.send_message(message.chat.id, 'Введите /start для запуска бота')

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        command = call.data
        tg_nick = call.message.chat.username
        user_id = call.message.chat.id
        if db_actions.user_is_existed(user_id):
            buttons = Bot_inline_btns()
            if db_actions.user_is_admin(user_id):
                if command == 'sync':
                    db_actions.update_config(sheet.config_excell())
                    db_actions.update_questions()
                    bot.send_message(user_id, 'Все тесты успешно загружены')
            if command[:10] == 'start_test':
                if temp_user_data.temp_data(user_id)[user_id][0] is None:
                    temp_user_data.temp_data(user_id)[user_id][1] = db_actions.get_id_quest_by_master(
                        command[10:])  # id вопросов [0, 1, 2]
                    temp_user_data.temp_data(user_id)[user_id][0] = 1
                    temp_user_data.temp_data(user_id)[user_id][2] = 0  # пройденных вопросов
                    temp_user_data.temp_data(user_id)[user_id][3] = command[10:]
                    temp_user_data.temp_data(user_id)[user_id][4] = True
                    text, quanity = get_question(temp_user_data.temp_data(user_id)[user_id][1][0], db_actions.get_questions_id_by_test_id(command[10:]))
                    bot.send_message(user_id, text, reply_markup=buttons.answer_btns(quanity))
            elif command[:8] == 'continue':
                if command[8:] in temp_user_data.temp_data(user_id)[user_id][1] and \
                        temp_user_data.temp_data(user_id)[user_id][0] is not None and \
                        len(temp_user_data.temp_data(user_id)[user_id][1]) - temp_user_data.temp_data(user_id)[user_id][
                    2] >= 0:
                    temp_user_data.temp_data(user_id)[user_id][4] = True
                    text, quanity = get_question(command[8:], db_actions.get_questions_id_by_test_id(temp_user_data.temp_data(user_id)[user_id][3]))
                    bot.send_message(user_id, text, reply_markup=buttons.answer_btns(quanity))
            elif command[:3] == 'end':
                if temp_user_data.temp_data(user_id)[user_id][0] is not None:
                    data = get_after_test(command[3:], tg_nick, user_id)
                    test_name = db_actions.get_test_name_by_id(temp_user_data.temp_data(user_id)[user_id][3])
                    marks = db_actions.get_marks_by_stat(test_name, f'https://t.me/{tg_nick}')
                    data = data.replace('{баллов}', f'{str(marks)} баллов')
                    temp_user_data.temp_data(user_id)[user_id][0] = None
                    bot.send_message(user_id, data, reply_markup=buttons.start_buttons('Найти новый тест'))
            elif command == 'tret':
                temp_user_data.temp_data(user_id)[user_id][0] = 0
                bot.send_message(user_id, f'Выберите тест введя его номер:\n{get_tests()}')
            elif command[:6] == 'answer' and temp_user_data.temp_data(user_id)[user_id][0] == 1:
                all_questions = len(temp_user_data.temp_data(user_id)[user_id][1])
                if all_questions - temp_user_data.temp_data(user_id)[user_id][2] >= 0 and \
                        temp_user_data.temp_data(user_id)[user_id][4]:
                    temp_user_data.temp_data(user_id)[user_id][2] += 1
                    index = temp_user_data.temp_data(user_id)[user_id][2] - 1
                    test_name = db_actions.get_test_name_by_id(temp_user_data.temp_data(user_id)[user_id][3])
                    marks = db_actions.get_marks_by_stat(test_name, f'https://t.me/{tg_nick}')
                    progress = round(100 * temp_user_data.temp_data(user_id)[user_id][2] / all_questions, 0)
                    current_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%d.%m.%Y')
                    after_quest, solve = db_actions.get_after_quest(temp_user_data.temp_data(user_id)[user_id][3],
                                                                    temp_user_data.temp_data(user_id)[user_id][1][
                                                                        index])
                    if index == 0:
                        marks = 0
                    temp_user_data.temp_data(user_id)[user_id][4] = False
                    if db_actions.check_correct(temp_user_data.temp_data(user_id)[user_id][1][index], command[6:], temp_user_data.temp_data(user_id)[user_id][3]):
                        row = db_actions.add_entry_statistic([current_time, progress, marks + 1], test_name,
                                                             f'https://t.me/{tg_nick}')
                        threading.Thread(target=db_actions.add_entry_statistic_excel([current_time, progress, marks + 1], test_name,
                                                             f'https://t.me/{tg_nick}', row)).start()
                        pre_text = after_quest[0].replace('{баллов}', f'{str(marks + 1)} баллов')
                        if all_questions != index + 1:
                            bot.send_photo(photo=after_quest[3], chat_id=user_id,
                                           caption=f'{pre_text}',
                                           reply_markup=buttons.contiue_test_btn(after_quest[2],
                                                                                 temp_user_data.temp_data(user_id)[
                                                                                     user_id][1][index + 1]))
                        else:
                            bot.send_photo(photo=after_quest[3], chat_id=user_id,
                                           caption=f'{pre_text}',
                                           reply_markup=buttons.end_test_btn(
                                               temp_user_data.temp_data(user_id)[user_id][3]))
                    else:
                        row = db_actions.add_entry_statistic([current_time, progress, marks], test_name,
                                                             f'https://t.me/{tg_nick}')
                        threading.Thread(
                            target=db_actions.add_entry_statistic_excel([current_time, progress, marks], test_name,
                                                                        f'https://t.me/{tg_nick}', row)).start()
                        pre_text = after_quest[1].replace('{баллов}', f'{str(marks)} баллов')
                        text = split_text(f'{pre_text}\n\n{solve}')
                        if all_questions != index + 1:
                            reply_markup = buttons.contiue_test_btn(after_quest[2], temp_user_data.temp_data(user_id)[
                                                                          user_id][1][index + 1])
                        else:
                            reply_markup = buttons.end_test_btn(temp_user_data.temp_data(user_id)[user_id][3])
                        for i in range(len(text)):
                            if len(text) == 1:
                                bot.send_photo(photo=after_quest[4], chat_id=user_id,
                                                   caption=text[i],
                                                   reply_markup=reply_markup)
                            elif i == 0:
                                bot.send_photo(photo=after_quest[4], chat_id=user_id, caption=text[i])
                            elif i+1 == len(text):
                                bot.send_message(user_id, text[i], reply_markup=reply_markup)
                            else:
                                bot.send_message(user_id, text[i])

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
