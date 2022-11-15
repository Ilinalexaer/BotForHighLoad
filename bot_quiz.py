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
    bot.send_message(message.chat.id, text="Правильно!")
    time.sleep(1)
    bot.send_message(message.chat.id, text=list_of_questions[number]['question_text'],
                     reply_markup=option_answers(list_of_questions[number]['option1'], list_of_questions[number]['option2'],
                                                 list_of_questions[number]['option3'], list_of_questions[number]['option4']))
    if list_of_questions[number]['picture']:
        bot.send_photo(message.chat.id, photo=open(list_of_questions[number]['picture'], 'rb'))

def wrong_answer(message, number):
    answers[list_of_questions[number-1]['question_text']] = message.text
    bot.send_message(message.chat.id, text=f"Неправильно\n\n{list_of_questions[number-1]['right_answer']}")
    #bot.send_message(message.chat.id, text=list_of_questions[number-1]['right_answer'])
    time.sleep(1)
    bot.send_message(message.chat.id, text=list_of_questions[number]['question_text'],
                     reply_markup=option_answers(list_of_questions[number]['option1'], list_of_questions[number]['option2'],
                                                 list_of_questions[number]['option3'], list_of_questions[number]['option4']))
    if list_of_questions[number]['picture']:
        bot.send_photo(message.chat.id, photo=open(list_of_questions[number]['picture'], 'rb'))


def result(count_of_answers, message):
    if count_of_answers < 4:
        bot.send_message(message.chat.id, text=f'Ты набрал {count_of_answers}')
        bot.send_photo(message.chat.id, photo=open('Alistair_Cockburn.jpg', 'rb'))
    elif count_of_answers >= 4 and count_of_answers <= 7:
        bot.send_message(message.chat.id, text=f'Ты набрал {count_of_answers}')
        bot.send_photo(message.chat.id, photo=open('Martin_Fowler.jpg', 'rb'))
    else:
        bot.send_message(message.chat.id, text=f'Ты набрал {count_of_answers} из 10')
        bot.send_photo(message.chat.id, photo=open('karl-weigers.png', 'rb'))

def db_write(message, answers):
    currentDateTime = datetime.datetime.now()
    conn = sqlite3.connect('quiz.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
            user_id TEXT PRIMARY KEY,
            chat_id TEXT,
            price TEXT,
            date TIMESTAMP);
            """)
    data_tuple = (str(uuid4()), f'{message.chat.username} {message.chat.last_name} {message.chat.first_name}',
                  str(answers), currentDateTime)
    cur.execute("INSERT INTO users VALUES(?, ?, ?, ?);", data_tuple)
    conn.commit()


count_of_answers = 0
answers = {}
@bot.message_handler(commands=['start'])
def start(message):
    global count_of_answers
    global answers
    count_of_answers = 0
    answers = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_start = types.KeyboardButton("🥳 Я в деле!")
    button_end = types.KeyboardButton("🤐 Давай в другой раз")
    markup.add(button_start).add(button_end)
    bot.send_message(message.chat.id, text="Привет\nПредлагаем тебе поучаствовать в викторине для системных и бизнес "
                                           "аналитиков от компании Звук", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    global count_of_answers
    global answers
    if message.text == "🤐 Давай в другой раз":
        bot.send_message(message.chat.id, text="Тогда лови ссылочку на нашу вакансию - https://hh.ru/vacancy/54389180")

    elif message.text == "🥳 Я в деле!":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_start = types.KeyboardButton("👊 Let's get ready to rumble!")
        markup.add(button_start)
        bot.send_message(message.chat.id, text="Викторина состоит из 10 вопросов. В каждом вопросе нужно выбрать "
                                               "один правильный ответ. Возможности ответить повторно у тебя нет, прости.\n"
                                               "Постарайся не ошибаться с выбором)\nЖелаю удачи!", reply_markup=markup)

        bot.send_photo(message.chat.id, photo=open('rumble.png', 'rb'))
    #первый вопрос------------------------------------------------------------------------------------------------
    elif message.text == "👊 Let's get ready to rumble!":
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
        bot.send_message(message.chat.id, text="Правильно!")
        time.sleep(1)
        result(count_of_answers, message)
        db_write(message, answers)
        end_of_quiz(message)

    elif (message.text not in right_answers) and (message.text in list_of_questions[9].values()):
        bot.send_message(message.chat.id, text=f"Неправильно")
        bot.send_message(message.chat.id, text=list_of_questions[9]['right_answer'])
        time.sleep(1)
        result(count_of_answers, message)
        db_write(message, answers)
        end_of_quiz(message)

    elif (message.text == '👍 Классно') or (message.text == '👎 Слабовато'):
        count_of_answers = 0
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_start = types.KeyboardButton("🥳 Я в деле!")
        button_end = types.KeyboardButton("🤐 Давай в другой раз")
        markup.add(button_start).add(button_end)
        bot.send_message(message.chat.id, text="Хочешь повторить?", reply_markup=markup)

    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммирован...")

bot.polling(none_stop=True, interval=0)