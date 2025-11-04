"""
ОБЩИЕ ФУНКЦИИ ДЛЯ ВСЕХ МОДУЛЕЙ
Функции, которые используются в нескольких модулях
"""

from telebot import types


def show_main_menu(bot, chat_id, user_name):
    """Показывает главное меню пользователя"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🔍 Найти клубы")
    btn2 = types.KeyboardButton("🎯 Мои клубы")
    btn3 = types.KeyboardButton("➕ Создать клуб")
    btn4 = types.KeyboardButton("👤 Мой профиль")
    markup.add(btn1, btn2, btn3, btn4)

    bot.send_message(chat_id, f"Привет, {user_name}! Что хочешь сделать?", reply_markup=markup)


def validate_name(name):
    """Проверяет валидность имени"""
    return len(name.strip()) >= 2


def validate_description(description):
    """Проверяет валидность описания"""
    return len(description.strip()) >= 10


def validate_telegram_link(link):
    """Проверяет валидность Telegram ссылки"""
    return link.strip().startswith('https://t.me/')