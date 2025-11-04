"""
ГЛАВНЫЙ ФАЙЛ БОТА - ТОЧКА ВХОДА
Регистрирует все обработчики и запускает бота
"""

import telebot
from telebot import types
from shared_functions import show_main_menu

# Импорт модулей
from modules.registration import register_registration_handlers
from modules.club_search import register_search_handlers
from modules.club_creation import register_creation_handlers
from modules.profile import register_profile_handlers
from modules.callbacks import register_callback_handlers

# Инициализация
bot = telebot.TeleBot('8362564410:AAEu48q8ps0MjyJf3PYLn_2E8Zj-aY-vDWI')
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
        show_main_menu(bot, message.chat.id, "Человек")
    else:
        bot.send_message(message.chat.id, "Используй кнопки меню для навигации 👆")

if __name__ == '__main__':
    print("🚀 Бот запущен...")
    bot.infinity_polling()

