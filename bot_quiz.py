import telebot
from telebot import types
import sqlite3
import os
import time
from dotenv import load_dotenv, find_dotenv
import random
from uuid import uuid4
import datetime
import json
import prettytable as pt

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('TOKEN'))

with open('source', 'r') as file1, open('answers', 'r') as file2:
    list_of_questions = [json.loads(i) for i in file1.readlines()]
    right_answers = [j.rstrip() for j in file2.readlines()]

random.shuffle(list_of_questions)


def option_answers(option1, option2, option3, option4):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_option1 = types.KeyboardButton(option1)
    button_option2 = types.KeyboardButton(option2)
    button_option3 = types.KeyboardButton(option3)
    button_option4 = types.KeyboardButton(option4)
    markup.add(button_option1, button_option2).add(button_option3, button_option4)
    return markup


def end_of_quiz(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_good = types.KeyboardButton('👍 Классно')
    button_bad = types.KeyboardButton('👎 Слабовато')
    markup.add(button_good).add(button_bad)
    bot.send_message(message.chat.id,
                     text="Спасибо за участие в нашей викторине.\nТебе зашло?", reply_markup=markup)
    return markup


def right_answer(message, number):
    global count_of_answers
    count_of_answers += 1
    answers[list_of_questions[number-1]['question_text']] = message.text
    bot.send_message(message.chat.id, text="✅Правильно!")
    time.sleep(1)
    bot.send_message(message.chat.id, text=list_of_questions[number]['question_text'],
                     reply_markup=option_answers(list_of_questions[number]['option1'], list_of_questions[number]['option2'],
                                                 list_of_questions[number]['option3'], list_of_questions[number]['option4']))
    if list_of_questions[number]['picture']:
        bot.send_photo(message.chat.id, photo=open(list_of_questions[number]['picture'], 'rb'))


def wrong_answer(message, number):
    answers[list_of_questions[number-1]['question_text']] = message.text
    #вариант с правильными ответами
    #bot.send_message(message.chat.id, text=f"⛔️Неправильно\n\n{list_of_questions[number-1]['right_answer']}")
    bot.send_message(message.chat.id, text="⛔️Неправильно!")
    time.sleep(1)
    bot.send_message(message.chat.id, text=list_of_questions[number]['question_text'],
                     reply_markup=option_answers(list_of_questions[number]['option1'], list_of_questions[number]['option2'],
                                                 list_of_questions[number]['option3'], list_of_questions[number]['option4']))
    if list_of_questions[number]['picture']:
        bot.send_photo(message.chat.id, photo=open(list_of_questions[number]['picture'], 'rb'))


def result(count_of_answers, message, time_spend):
    if count_of_answers < 4:
        bot.send_message(message.chat.id, text=f'🎯 ты набрал {count_of_answers} из 10')
        bot.send_message(message.chat.id, text=f"⏱ твоё время - {int(time_spend//60)} мин {round(time_spend%60, 2)}с")
        bot.send_photo(message.chat.id, photo=open('bad.jpeg', 'rb'))
    elif count_of_answers >= 4 and count_of_answers <= 7:
        bot.send_message(message.chat.id, text=f'🎯 ты набрал {count_of_answers} из 10')
        bot.send_message(message.chat.id, text=f"⏱ твоё время - {int(time_spend//60)} мин {round(time_spend%60, 2)}с")
        bot.send_photo(message.chat.id, photo=open('good.jpeg', 'rb'))
    else:
        bot.send_message(message.chat.id, text=f'🎯 ты набрал {count_of_answers} из 10')
        bot.send_message(message.chat.id, text=f"⏱ твоё время - {int(time_spend//60)} мин {round(time_spend%60, 2)}с")
        bot.send_photo(message.chat.id, photo=open('amazing.jpeg', 'rb'))


def db_check_user(message):
    conn = sqlite3.connect('quiz.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
            uuid TEXT PRIMARY KEY,
            user_id TEXT,
            user_name TEXT,
            user_last_name TEXT,
            user_first_name TEXT,
            answers TEXT,
            right_answers INTEGER,
            time REAL,
            date TIMESTAMP);
            """)

    cur.execute(f'SELECT * FROM users WHERE user_id = {message.from_user.id}')
    if cur.fetchall():
        return False
    else:
        return True


def db_write(message, answers, count_of_answers, time_spend):
    currentDateTime = datetime.datetime.now()
    conn = sqlite3.connect('quiz.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
            uuid TEXT PRIMARY KEY,
            user_id TEXT,
            user_name TEXT,
            user_last_name TEXT,
            user_first_name TEXT,
            answers TEXT,
            right_answers INTEGER,
            time REAL,
            date TIMESTAMP);
            """)
    data_tuple = (str(uuid4()), message.from_user.id, message.chat.username, message.chat.last_name,
                  message.chat.first_name, str(answers), int(count_of_answers), time_spend, currentDateTime)
    cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?);", data_tuple)
    conn.commit()


def db_show_result():
    conn = sqlite3.connect('quiz.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
            uuid TEXT PRIMARY KEY,
            user_id TEXT,
            user_name TEXT,
            user_last_name TEXT,
            user_first_name TEXT,
            answers TEXT,
            right_answers INTEGER,
            time REAL,
            date TIMESTAMP);
            """)

    result = cur.execute('SELECT user_name, user_last_name, user_first_name, right_answers, time '
                'FROM users '
                'ORDER BY right_answers DESC, time ASC')
    return result


def table_quiz():
    table = pt.PrettyTable(['Nike', 'LastName', 'FirstName', 'Answers', 'TimeSpent'])
    for user_name,  user_last_name, user_first_name, answers, time in db_show_result():
        table.add_row([user_name, user_last_name, user_first_name, f'{answers:.4f}', f'{time:.5f}'])
    return table


count_of_answers = 0
answers = {}
@bot.message_handler(commands=['start'])
def start(message):
    #global count_of_answers
    #global answers
    count_of_answers = 0
    answers = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_start = types.KeyboardButton("🥳 Я в деле!")
    button_end = types.KeyboardButton("🤐 Давай в другой раз")
    markup.add(button_start).add(button_end)
    bot.send_message(message.chat.id, text="Привет!\nПредлагаем тебе поучаствовать в викторине для системных и бизнес "
                                           "аналитиков от компании Звук", reply_markup=markup, parse_mode='HTML')


@bot.message_handler(content_types=['text'])
def func(message):
    global count_of_answers
    global answers
    global start_time
    if (message.text == "🤐 Давай в другой раз") or (message.text == '❤️ Наша вакансия'):
        bot.send_message(message.chat.id, text="Наша вакансия\nhttps://hh.ru/vacancy/54389180")

    elif (message.text == "🥳 Я в деле!") and (db_check_user(message)):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_start = types.KeyboardButton("👊 Let's get ready to rumble!")
        markup.add(button_start)
        bot.send_message(message.chat.id, text="🔹<b>Викторина состоит из 10 вопросов</b>\n🔹<b>В каждом вопросе нужно выбрать "
                                               "один правильный ответ</b>\n🔹<b>Время прохождения также учитывается</b>\n"
                                               "🔹<b>Пройти викторину можно только один раз</b>\n\n"
                                               "Постарайся не ошибаться с выбором)\nЖелаю удачи!",
                         reply_markup=markup, parse_mode='HTML')

        bot.send_photo(message.chat.id, photo=open('ready.jpeg', 'rb'))

    elif (message.text == "🥳 Я в деле!") and (db_check_user(message) == False):
        bot.send_message(message.chat.id, text="Ты уже проходил🤷")

    #первый вопрос------------------------------------------------------------------------------------------------
    elif message.text == ("👊 Let's get ready to rumble!") and (db_check_user(message)):
        start_time = time.time()
        time.sleep(1)
        bot.send_message(message.chat.id, text=list_of_questions[0]['question_text'],
                             reply_markup=option_answers(list_of_questions[0]['option1'], list_of_questions[0]['option2'],
                                                         list_of_questions[0]['option3'], list_of_questions[0]['option4']))
        if list_of_questions[0]['picture']:
            bot.send_photo(message.chat.id, photo=open(list_of_questions[0]['picture'], 'rb'))
    #второй вопрос------------------------------------------------------------------------------------------------
    elif (message.text in right_answers) and (message.text in list_of_questions[0].values()):
        right_answer(message, 1)

    elif (message.text not in right_answers) and (message.text in list_of_questions[0].values()):
        wrong_answer(message, 1)

    #третий ворос------------------------------------------------------------------------------------------------
    elif (message.text in right_answers) and (message.text in list_of_questions[1].values()):
        right_answer(message, 2)

    elif (message.text not in right_answers) and (message.text in list_of_questions[1].values()):
        wrong_answer(message, 2)

    # четвертый вопрос------------------------------------------------------------------------------------------------
    elif (message.text in right_answers) and (message.text in list_of_questions[2].values()):
        right_answer(message, 3)

    elif (message.text not in right_answers) and (message.text in list_of_questions[2].values()):
        wrong_answer(message, 3)

    # пятый вопрос------------------------------------------------------------------------------------------------
    elif (message.text in right_answers) and (message.text in list_of_questions[3].values()):
        right_answer(message, 4)

    elif (message.text not in right_answers) and (message.text in list_of_questions[3].values()):
        wrong_answer(message, 4)

    # шестой вопрос------------------------------------------------------------------------------------------------
    elif (message.text in right_answers) and (message.text in list_of_questions[4].values()):
        right_answer(message, 5)

    elif (message.text not in right_answers) and (message.text in list_of_questions[4].values()):
        wrong_answer(message, 5)

    #седьмой вопрос------------------------------------------------------------------------------------------------
    elif (message.text in right_answers) and (message.text in list_of_questions[5].values()):
        right_answer(message, 6)

    elif (message.text not in right_answers) and (message.text in list_of_questions[5].values()):
        wrong_answer(message, 6)

    #восьмой вопрос------------------------------------------------------------------------------------------------
    elif (message.text in right_answers) and (message.text in list_of_questions[6].values()):
        right_answer(message, 7)

    elif (message.text not in right_answers) and (message.text in list_of_questions[6].values()):
        wrong_answer(message, 7)

    #девятый вопрос------------------------------------------------------------------------------------------------
    elif (message.text in right_answers) and (message.text in list_of_questions[7].values()):
        right_answer(message, 8)

    elif (message.text not in right_answers) and (message.text in list_of_questions[7].values()):
        wrong_answer(message, 8)

    #десятый вопрос------------------------------------------------------------------------------------------------
    elif (message.text in right_answers) and (message.text in list_of_questions[8].values()):
        right_answer(message, 9)

    elif (message.text not in right_answers) and (message.text in list_of_questions[8].values()):
        wrong_answer(message, 9)

    #последний ответ--------------------------- --------------------------------------------------------------------
    elif (message.text in right_answers) and (message.text in list_of_questions[9].values()):
        count_of_answers += 1
        bot.send_message(message.chat.id, text="✅Правильно!")
        time.sleep(1)

        time_spend = round(time.time() - start_time, 3)
        result(count_of_answers, message, time_spend)

        #bot.send_message(message.chat.id, text=f"Ваше время - {time_spend}")
        db_write(message, answers, count_of_answers, time_spend)
        end_of_quiz(message)

    elif (message.text not in right_answers) and (message.text in list_of_questions[9].values()):
        bot.send_message(message.chat.id, text="⛔️Неправильно")
        #bot.send_message(message.chat.id, text=list_of_questions[9]['right_answer'])
        time.sleep(1)
        time_spend = round(time.time() - start_time, 3)
        result(count_of_answers, message, time_spend)
        #bot.send_message(message.chat.id, text=f"Ваше время - {time_spend}")
        db_write(message, answers, count_of_answers, time_spend)
        end_of_quiz(message)

    elif (message.text == '👎 Слабовато'):
        count_of_answers = 0
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_start = types.KeyboardButton("❤️ Наша вакансия")
        markup.add(button_start)
        bot.send_message(message.chat.id, text="Ты крут, присоединяйся к команде Звука", reply_markup=markup)

    elif (message.text == '👍 Классно'):
        count_of_answers = 0
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_start = types.KeyboardButton("❤️ Наша вакансия")
        markup.add(button_start)
        bot.send_message(message.chat.id, text="Присоединяйся к команде Звука", reply_markup=markup)

    elif (message.text == 'Результаты'):
        with open('result.html', 'w') as f:
            f.write(f'<pre>{table_quiz()}</pre>')
        bot.send_document(message.chat.id, open('result.html', 'rb'))

    else:
        bot.send_message(message.chat.id, text="Нет такой команды...")

bot.polling(none_stop=True, interval=0)