"""
МОДУЛЬ РЕГИСТРАЦИИ И АВТОРИЗАЦИИ
Обработка команды /start, регистрация новых пользователей
"""

from telebot import types
import database
from shared_functions import show_main_menu, validate_name


def register_registration_handlers(bot, user_states):
    """Регистрирует обработчики регистрации"""

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        """Обработчик команды /start"""
        user = database.get_user_by_tg_id(message.from_user.id)

        if not user:
            # Новый пользователь - начинаем регистрацию
            msg = bot.send_message(message.chat.id, "Привет! Давай зарегистрируем тебя. Как тебя зовут?")
            bot.register_next_step_handler(msg, process_registration_name)
        else:
            # Существующий пользователь - показываем меню
            show_main_menu(bot, message.chat.id, user['name'])

    def process_registration_name(message):
        """Обработка ввода имени при регистрации"""
        name = message.text.strip()

        if not validate_name(name):
            msg = bot.send_message(message.chat.id, "Имя слишком короткое. Введите нормальное имя:")
            bot.register_next_step_handler(msg, process_registration_name)
            return

        tg_id = message.from_user.id
        username = message.from_user.username

        # Создаем пользователя в БД
        success = database.create_user(tg_id, name, username)
        if success:
            bot.send_message(message.chat.id, f"Отлично, {name}! Регистрация завершена.")
            show_main_menu(bot, message.chat.id, name)
        else:
            bot.send_message(message.chat.id, "Что-то пошло не так. Попробуй еще раз /start")

    # Возвращаем функции для использования в других модулях
    return {
        'show_main_menu': show_main_menu,
        'process_registration_name': process_registration_name
    }
