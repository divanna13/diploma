import telebot
from telebot import types
from telebot.util import quick_markup
import logging
import models

# Set up logging for the bot
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# singer_children_bot
API_TOKEN = '7686258574:AAHDcexxxffu3lZ8-ddAon-UTpPWWQpreuQ'
ADMIN_ID = 52919873 # YuryB
# ADMIN_ID = 664987030 # Anna


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
        markup = quick_markup({
            f'Новых детей {len(models.Children().ungrouped())}': {'callback_data': 'new_childrens'},
            f'Дет.Сады {len(models.Garden().all())}': {'callback_data': 'gardens'},
            'Группы': {'callback_data': 'groups'},            
            'Посещения': {'callback_data': 'attendings'},
            'Оплаты': {'callback_data': 'payments'},
        }, row_width=2)
        bot.send_message(message.chat.id, "Здравствуйте, администратор бота!\nВыберите команду:", reply_markup=markup)
        bot.clear_step_handler_by_chat_id(message.chat.id)

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
            child.insert(child_name, parent_id, 0) # group_id = 0 недобавленный ребенок
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

# Добавление АДМИНОМ садиков
@bot.callback_query_handler(func=lambda call: True)
def handle_query(cb):
    if cb.from_user.id == ADMIN_ID:
        if cb.data == "gardens":
            gardens = models.Garden().all()
            if len(gardens) > 0:
                bot.send_message(cb.from_user.id,"Существующие садики:")
                for g in gardens:
                    bot.send_message(cb.from_user.id, ' - '+g[1])
            else:
                bot.send_message(cb.from_user.id,"Нет добавленных садиков! Начните добавлять!")

            markup = quick_markup({'Возврат в главное меню': {'callback_data': '/start'}}, row_width=1)                
            bot.send_message(cb.from_user.id,"Чтобы добавить новый садик введите имя садика и его номер и нажмите отправить:", reply_markup=markup)
            bot.register_next_step_handler(cb.message, process_garden_name_step)           

        if cb.data == "groups":
            models.Group()
            gardens = models.Garden().all_with_groups_dict()  
            # Добавить вывод списка групп для садиков, переменная gardens содержит массив словарей
            # [{garden_id: 1, garden_name: "Прекрасный Сад Будущего №5", price: 100, group_name: "Скворцы", group_id: 1}, ...]
            if len(gardens) > 0:
                bot.send_message(cb.from_user.id,"Существующие садики/группы:")
                for g in gardens:
                    bot.send_message(cb.from_user.id, f' - {g["garden_name"]} / {g["group_name"]} ({g["price"]} ₽)')
            else:
                bot.send_message(cb.from_user.id,"Нет добавленных садиков и групп! Начните добавлять!")

def process_garden_name_step(message):
    try:
        chat_id = message.chat.id
        if message.from_user.id != ADMIN_ID:
            bot.reply_to(message, 'Только Админ может добавлять садики!')
        else:
            name = message.text
            models.Garden().insert(name)            
            bot.register_next_step_handler(message, send_welcome)
            bot.reply_to(message, f'Вы добавили садик: {name}. Возврат в главное меню')
    except Exception as e:
        logging.critical(e, exc_info=True)
        bot.reply_to(message, 'Ошибка!')



# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()
bot.infinity_polling()