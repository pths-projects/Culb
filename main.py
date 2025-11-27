"""
ГЛАВНЫЙ ФАЙЛ БОТА - ТОЧКА ВХОДА
Регистрирует все обработчики и запускает бота
"""

import os
from dotenv import load_dotenv
import telebot
from telebot import types

# Инициализация базы данных
from utils.databases import make_engine
from orm_models.users import Base

# Импорт модулей
from modules.registration import register_registration_handlers
from modules.club_search import register_search_handlers
from modules.club_creation import register_creation_handlers
from modules.profile import register_profile_handlers
from modules.callbacks import register_callback_handlers
from shared_functions import show_main_menu

# Загружаем переменные окружения из .env файла
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Инициализация БД
def initialize_database():
    """Инициализирует базу данных - создает таблицы если их нет"""
    engine = make_engine()
    Base.metadata.create_all(engine)
    print("✅ База данных инициализирована в облаке (PostgreSQL)")

# Инициализация
initialize_database()
bot = telebot.TeleBot(TELEGRAM_TOKEN)
user_states = {}

# Регистрация всех обработчиков
registration_handlers = register_registration_handlers(bot, user_states)
search_handlers = register_search_handlers(bot, user_states)
creation_handlers = register_creation_handlers(bot, user_states, registration_handlers['show_main_menu'])
profile_handlers = register_profile_handlers(bot, user_states)
callback_handlers = register_callback_handlers(bot, user_states, search_handlers, profile_handlers)

# Fallback обработчик
@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    if message.text == "❌ Отмена":
        bot.send_message(message.chat.id, "Действие отменено", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "Используй кнопки меню для навигации 👆")

if __name__ == '__main__':
    print("🚀 Бот запущен...")
    bot.infinity_polling()

