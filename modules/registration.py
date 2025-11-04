"""
МОДУЛЬ РЕГИСТРАЦИИ И АВТОРИЗАЦИИ
Обработка команды /start, регистрация новых пользователей
"""

from telebot import types
from shared_functions import show_main_menu, validate_name


def register_registration_handlers(bot, user_states):
    """Регистрирует обработчики регистрации"""

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        """Обработчик команды /start"""
        bot.send_message(message.chat.id, "Привет, Человек, ты зарегистрирован")
        show_main_menu(bot, message.chat.id, "Человек")

    # Возвращаем функции для использования в других модулях
    return {
        'show_main_menu': show_main_menu
    }
