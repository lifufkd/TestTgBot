#####################################
#            Created by             #
#                SBR                #
#               zzsxd               #
#####################################
import copy
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


def get_question(test_id, quest_id, test_id_select, user_id, index=0):
    out = list()
    s = ''
    name, questions = db_actions.get_question(test_id, quest_id)
    quest_start = db_actions.get_start_question(test_id_select)
    quest_start = quest_start.replace('{Вопрос}', f'{str(get_number_question(user_id, index))}')
    s += f'{quest_start}{name[0]}'
    out.append(s)
    out.append(name[1])
    return out, questions


def get_number_question(user_id, index=0):
    if temp_user_data.temp_data(user_id)[user_id][7]:
        return temp_user_data.temp_data(user_id)[user_id][6][index-temp_user_data.temp_data(user_id)[user_id][8]]
    else:
        return temp_user_data.temp_data(user_id)[user_id][2] + 1


def split_text(text):
    sentence_endings = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
    sentences = re.split(sentence_endings, text)
    result = []
    current_line = ''
    for sentence in sentences:
        if len(current_line) + len(sentence)+1 <= 1000:
            current_line += f' {sentence}'
        else:
            result.append(current_line)
            current_line = f' {sentence}'
    if current_line:
        result.append(current_line)
    return result


def get_after_test(test_id, user_nick, user_id):
    data = db_actions.get_requiem(test_id)
    marks = db_actions.get_marks_by_stat(db_actions.get_test_name_by_ids(test_id),
                                                         f'https://t.me/{user_nick}')
    data = data.replace('#{баллов}',
                        str(marks))
    data = data.replace('#{вопросов_всего}', str(len(temp_user_data.temp_data(user_id)[user_id][5])+marks))
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
            temp_user_data.temp_data(user_id)[user_id][0] = 0
            data = db_actions.get_all_tests()
            bot.send_message(user_id, f'Выберите тест:', reply_markup=buttons.first_btns(data), parse_mode='HTML')
        elif command[:5] == 'start':
            quanity, data = db_actions.command_run(command[6:])
            if quanity and data is not None:
                temp_user_data.temp_data(user_id)[user_id][0] = None
                bot.send_message(user_id, f'{data[1]}',
                                 reply_markup=buttons.start_test_btn(data[3], data[4]), parse_mode='HTML')
            else:
                bot.send_message(user_id, 'Тест не существует', parse_mode='HTML')

    @bot.message_handler(commands=['admin'])
    def tovar_msg(message):
        command = message.text.replace('/', '')
        user_id = message.chat.id
        if db_actions.user_is_existed(user_id):
            buttons = Bot_inline_btns()
            if db_actions.user_is_admin(user_id):
                if command == 'admin':
                    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}!\n',
                                     reply_markup=buttons.admin_btns(), parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'Введите /start для запуска бота', parse_mode='HTML')

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
                    bot.send_message(user_id, 'Все тесты успешно загружены', parse_mode='HTML')
            if command[:10] == 'start_test':
                if temp_user_data.temp_data(user_id)[user_id][0] is None:
                    temp_user_data.temp_data(user_id)[user_id][1] = db_actions.get_id_quest_by_master(
                        command[10:])  # id вопросов [0, 1, 2]
                    temp_user_data.temp_data(user_id)[user_id][0] = 1
                    temp_user_data.temp_data(user_id)[user_id][2] = 0  # пройденных вопросов
                    temp_user_data.temp_data(user_id)[user_id][3] = command[10:]
                    temp_user_data.temp_data(user_id)[user_id][4] = True
                    temp_user_data.temp_data(user_id)[user_id][8] = 0
                    text, quanity = get_question(temp_user_data.temp_data(user_id)[user_id][1][0], db_actions.get_questions_id_by_test_id(command[10:]), command[10:], user_id)
                    bot.send_message(user_id, text[0], reply_markup=buttons.answer_btns(quanity, text[1]), parse_mode='HTML')
            elif command[:8] == 'continue':
                if command[8:] in temp_user_data.temp_data(user_id)[user_id][1] and \
                        temp_user_data.temp_data(user_id)[user_id][0] is not None and \
                        len(temp_user_data.temp_data(user_id)[user_id][1]) - temp_user_data.temp_data(user_id)[user_id][
                    2] >= 0:
                    if not temp_user_data.temp_data(user_id)[user_id][7]:
                        index = temp_user_data.temp_data(user_id)[user_id][2] + 1
                    else:
                        index = temp_user_data.temp_data(user_id)[user_id][2]
                    temp_user_data.temp_data(user_id)[user_id][4] = True
                    text, quanity = get_question(command[8:], db_actions.get_questions_id_by_test_id(temp_user_data.temp_data(user_id)[user_id][3]), temp_user_data.temp_data(user_id)[user_id][3], user_id, index)
                    bot.send_message(user_id, text[0], reply_markup=buttons.answer_btns(quanity, text[1]), parse_mode='HTML')
            elif command[:4] == 'test':
                temp_user_data.temp_data(user_id)[user_id][0] = None
                quanity, data = db_actions.pre_test_data(command[4:])
                bot.send_message(user_id, f'{data[1]}',
                                 reply_markup=buttons.start_test_btn(data[3], command[4:]), parse_mode='HTML')
            elif command[:3] == 'end':
                if temp_user_data.temp_data(user_id)[user_id][0] is not None:
                    data = get_after_test(command[3:], tg_nick, user_id)
                    test_name = db_actions.get_test_name_by_id(temp_user_data.temp_data(user_id)[user_id][3])
                    marks = db_actions.get_marks_by_stat(test_name, f'https://t.me/{tg_nick}')
                    data = data.replace('{баллов}', f'{str(marks)}')
                    temp_user_data.temp_data(user_id)[user_id][0] = None
                    temp_user_data.temp_data(user_id)[user_id][5] = copy.deepcopy([])
                    temp_user_data.temp_data(user_id)[user_id][6] = copy.deepcopy([])
                    temp_user_data.temp_data(user_id)[user_id][7] = False
                    end_text = db_actions.get_questions_end_btn(temp_user_data.temp_data(user_id)[user_id][3])
                    bot.send_message(user_id, data, reply_markup=buttons.start_buttons(end_text[0]), parse_mode='HTML')
            elif command[:5] == 'tret':
                temp_user_data.temp_data(user_id)[user_id][0] = 0
                data = db_actions.get_all_tests()
                bot.send_message(user_id, f'Выберите тест:', reply_markup=buttons.first_btns(data), parse_mode='HTML')
            elif command[:5] == 'again':
                if temp_user_data.temp_data(user_id)[user_id][0] is not None:
                    temp_user_data.temp_data(user_id)[user_id][1] = copy.deepcopy(temp_user_data.temp_data(user_id)[user_id][5])
                    temp_user_data.temp_data(user_id)[user_id][2] = 0  # пройденных вопросов
                    temp_user_data.temp_data(user_id)[user_id][4] = True
                    temp_user_data.temp_data(user_id)[user_id][7] = True
                    temp_user_data.temp_data(user_id)[user_id][8] = 0
                    print(temp_user_data.temp_data(user_id)[user_id][5])
                    print(temp_user_data.temp_data(user_id)[user_id][6])
                    text, quanity = get_question(temp_user_data.temp_data(user_id)[user_id][1][0],
                                                 db_actions.get_questions_id_by_test_id(temp_user_data.temp_data(user_id)[user_id][3]),
                                                 temp_user_data.temp_data(user_id)[user_id][3], user_id, 0)
                    bot.send_message(user_id, text[0], reply_markup=buttons.answer_btns(quanity, text[1]),
                                     parse_mode='HTML')
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
                    if index == 0 and not temp_user_data.temp_data(user_id)[user_id][7]:
                        marks = 0
                    temp_user_data.temp_data(user_id)[user_id][4] = False
                    if db_actions.check_correct(temp_user_data.temp_data(user_id)[user_id][1][index], command[6:], temp_user_data.temp_data(user_id)[user_id][3]):
                        question_number = get_number_question(user_id, index)
                        if not temp_user_data.temp_data(user_id)[user_id][7]:
                            question_number -= 1
                        if temp_user_data.temp_data(user_id)[user_id][7]:
                            temp_user_data.temp_data(user_id)[user_id][5].remove(temp_user_data.temp_data(user_id)[user_id][1][index])
                            temp_user_data.temp_data(user_id)[user_id][6].remove(question_number)
                            temp_user_data.temp_data(user_id)[user_id][8] += 1
                        if len(temp_user_data.temp_data(user_id)[user_id][5]) == 0:
                            stat = False
                        else:
                            stat = True
                        row = db_actions.add_entry_statistic([current_time, progress, marks + 1], test_name,
                                                             f'https://t.me/{tg_nick}')
                        threading.Thread(target=db_actions.add_entry_statistic_excel, args=([current_time, progress, marks + 1], test_name,
                                                             f'https://t.me/{tg_nick}', row)).start()
                        data = after_quest[5] + after_quest[0]
                        pre_text = data.replace('{баллов}', f'{str(marks + 1)}')
                        pre_text = pre_text.replace('{Вопрос}', f'{str(question_number)}')
                        end_text = db_actions.get_questions_end_btn(temp_user_data.temp_data(user_id)[user_id][3])
                        if all_questions != index + 1:
                            if len(after_quest[3]) != 0:
                                bot.send_photo(photo=after_quest[3], chat_id=user_id,
                                               caption=f'{pre_text}',
                                               reply_markup=buttons.contiue_test_btn(after_quest[2],
                                                                                     temp_user_data.temp_data(user_id)[
                                                                                         user_id][1][index + 1]), parse_mode='HTML')
                            else:
                                bot.send_message(chat_id=user_id,
                                               text=f'{pre_text}',
                                               reply_markup=buttons.contiue_test_btn(after_quest[2],
                                                                                     temp_user_data.temp_data(user_id)[
                                                                                         user_id][1][index + 1]),
                                               parse_mode='HTML')
                        else:
                            if len(after_quest[3]) != 0:
                                bot.send_photo(photo=after_quest[3], chat_id=user_id,
                                               caption=f'{pre_text}',
                                               reply_markup=buttons.end_test_btn(
                                                   temp_user_data.temp_data(user_id)[user_id][3], end_text[0], end_text[1], stat), parse_mode='HTML')
                            else:
                                bot.send_message(chat_id=user_id,
                                               text=f'{pre_text}',
                                               reply_markup=buttons.end_test_btn(
                                                   temp_user_data.temp_data(user_id)[user_id][3], end_text[0], end_text[1], stat), parse_mode='HTML')
                    else:
                        row = db_actions.add_entry_statistic([current_time, progress, marks], test_name,
                                                             f'https://t.me/{tg_nick}')
                        threading.Thread(
                            target=db_actions.add_entry_statistic_excel, args=([current_time, progress, marks], test_name,
                                                                        f'https://t.me/{tg_nick}', row)).start()
                        question_number = get_number_question(user_id, index)
                        if not temp_user_data.temp_data(user_id)[user_id][7]:
                            question_number -= 1
                        if len(temp_user_data.temp_data(user_id)[user_id][5]) == 0:
                            stat = False
                        else:
                            stat = True
                        if temp_user_data.temp_data(user_id)[user_id][1][index] not in temp_user_data.temp_data(user_id)[user_id][5]:
                            temp_user_data.temp_data(user_id)[user_id][5].append(temp_user_data.temp_data(user_id)[user_id][1][index])
                        if temp_user_data.temp_data(user_id)[user_id][2] not in temp_user_data.temp_data(user_id)[user_id][6]:
                            temp_user_data.temp_data(user_id)[user_id][6].append(temp_user_data.temp_data(user_id)[user_id][2])
                        data = after_quest[5] + after_quest[1]
                        pre_text = data.replace('{баллов}', f'{str(marks + 1)}')
                        if not temp_user_data.temp_data(user_id)[user_id][7]:
                            pre_text = pre_text.replace('{Вопрос}', f'{str(question_number)}')
                        else:
                            pre_text = pre_text.replace('{Вопрос}', f'{str(question_number)}')
                        end_text = db_actions.get_questions_end_btn(temp_user_data.temp_data(user_id)[user_id][3])
                        text = split_text(f'{pre_text}\n\n{solve}')
                        if all_questions != index + 1:
                            reply_markup = buttons.contiue_test_btn(after_quest[2], temp_user_data.temp_data(user_id)[
                                                                          user_id][1][index + 1])
                        else:
                            reply_markup = buttons.end_test_btn(temp_user_data.temp_data(user_id)[user_id][3], end_text[0], end_text[1], stat)
                        for i in range(len(text)):
                            if len(text) == 1:
                                if len(after_quest[4]) != 0:
                                    bot.send_photo(photo=after_quest[4], chat_id=user_id,
                                                       caption=text[i],
                                                       reply_markup=reply_markup, parse_mode='HTML')
                                else:
                                    bot.send_message(chat_id=user_id,
                                                   text=text[i],
                                                   reply_markup=reply_markup, parse_mode='HTML')
                            elif i == 0:
                                if len(after_quest[4]) != 0:
                                    bot.send_photo(photo=after_quest[4], chat_id=user_id, caption=text[i], parse_mode='HTML')
                                else:
                                    bot.send_message(chat_id=user_id,
                                                     text=text[i], parse_mode='HTML')
                            elif i+1 == len(text):
                                bot.send_message(user_id, text[i], reply_markup=reply_markup, parse_mode='HTML')
                            else:
                                bot.send_message(user_id, text[i], parse_mode='HTML')

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
