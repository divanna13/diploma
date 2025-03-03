import telebot
from telebot import types
from telebot.util import quick_markup
import logging
import models

logging.basicConfig(level=logging.INFO)


# singer_children_bot
API_TOKEN = '7686258574:AAHDcexxxffu3lZ8-ddAon-UTpPWWQpreuQ'
ADMIN_ID = 0000000


bot = telebot.TeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, """  
Здравствуйте, вы подключили бот для записи вашего ребенка или детей на занятия по хоровому пению.
        
Введите фамилию имя ребенка, например: Иванов Иван и нажмите кнопку отправить.
""")
        parent = models.Parent()
        fio = (message.from_user.first_name or "") + " " + (message.from_user.last_name or "")
        parent.insert(message.from_user.id, message.from_user.username, fio, "")
    else: # ADMIN
        bot.reply(message, "Вы -- админ")

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def parse_message(message):
    if message.from_user.id != ADMIN_ID:
        child_name = message.text        
        markup = quick_markup({
            'Чмокнуть': {'callback_data': 'chmok_child'},
            'Удалить': {'callback_data': 'delete_child'}
        }, row_width=2)
        if child_name != "":
            child = models.Children()       
            parent_id = models.Parent().find_by_tg_id(message.from_user.id)            
            child.insert(child_name, parent_id, 0)
            bot.reply_to(message, f"Вы добавили ребенка: {child_name}",reply_markup=markup)
        bot.send_message(message.chat.id, """       
Введите фамилию имя ребенка, например: Иванов Иван и нажмите кнопку отправить.
""")

@bot.message_handler(commands=['button'])
def button_message(message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Кнопка")
    markup.add(item1)
    bot.send_message(message.chat.id,'Выберите что вам надо',reply_markup=markup)

@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text=="Кнопка":
        bot.send_message(message.chat.id,"https://divaeva.ru")



bot.infinity_polling()