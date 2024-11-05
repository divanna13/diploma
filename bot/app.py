import telebot
from telebot import types
from datetime import datetime
import pandas as pd
import sqlite3

class Connect():
    def __init__(self, name:str) -> None:
        self.connection = sqlite3.connect(name)
        self.cursor = self.connection.cursor()
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS Letters (
                   user_id INTEGER PRIMARY KEY,
                   telegram_id INTEGER,
                   fio TEXT NOT NULL,
                   letter TEXT NOT NULL,
                   date TEXT
            )
        ''')
        self.connection.commit()
                    
    def insert(self, telegram_id:int, fio:str, letter:str, date:str) -> None:
        self.cursor = self.connection.cursor()
        self.cursor.execute('INSERT INTO Letters (telegram_id, fio, letter, date) VALUES (?, ?, ?, ?)', (telegram_id, fio, letter, date))
        self.connection.commit()
    
    def __del__(self):
        self.connection.close()

token:str = ''
bot=telebot.TeleBot(token)
users:dict = {}


@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id:int = message.chat.id
    users[chat_id] = {}
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [
                types.KeyboardButton("Написать письмо в капсулу времени"),
                types.KeyboardButton("Выгрузить данные в XLS")
            ]
    keyboard.add(*buttons)
    bot.send_message(chat_id, "Привет!", reply_markup=keyboard)
    
@bot.message_handler(content_types='text')
def choose(message):
    if message.text == 'Написать письмо в капсулу времени':
        bot.send_message(message.chat.id, 'Введите вашу фамилию, имя, отчество')
        bot.register_next_step_handler(message, save_fio)
    if message.text == 'Написать послание':
        bot.send_message(message.chat.id, 'Введите ваше послание')
        bot.register_next_step_handler(message, save_letter)
    if message.text == 'Сохранить':
        telegram_id:int = message.chat.id
        fio:str = users[telegram_id]['fio']
        letter:str = users[telegram_id]["letter"]
        date = datetime.now().strftime('%d/%m/%Y, %H:%M')
        connect = Connect('database.db')
        connect.insert(telegram_id, fio, letter, date)
        bot.send_message(message.chat.id, 'Спасибо! Ваша капсула сохранена!')
        start_message(message) 
    if message.text == 'Выгрузить данные в XLS':
        connect = Connect('database.db')
        conn = connect.connection
        df = pd.read_sql('select * from Letters', conn)
        df.to_excel('result.xlsx', index=False)
        bot.send_message(message.chat.id, 'Данные выгружены.')
        file = open('result.xlsx', 'rb')
        bot.send_document(message.chat.id, file)
    if message.text == 'Отмена':
        start_message(message)  
    
        
def save_fio(message):
    chat_id:int = message.chat.id
    fio:str = message.text
    users[chat_id]['fio'] = fio
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [
                types.KeyboardButton("Написать послание"), 
                types.KeyboardButton("Отмена")
            ]
    keyboard.add(*buttons)
    bot.send_message(chat_id, 'Выберите:', reply_markup=keyboard)
            
def save_letter(message):
    chat_id:int = message.chat.id
    letter:str = message.text
    users[chat_id]['letter'] = letter
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = [
                types.KeyboardButton("Сохранить"),
                types.KeyboardButton("Отмена")
            ]
    keyboard.add(*buttons)
    bot.send_message(chat_id, f'ФИО:    {users[chat_id]["fio"]}\nПисьмо:    {users[chat_id]["letter"]}\n', reply_markup=keyboard)

if __name__ == '__main__':
    print('Бот запущен!')
    bot.polling()
