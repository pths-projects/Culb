"""
МОДУЛЬ ПОИСКА И ПРОСМОТРА КЛУБОВ
Поиск клубов по тегам, локации, просмотр деталей клуба
"""

from telebot import types
from shared_functions import show_main_menu

def register_search_handlers(bot, user_states):
    """Регистрирует обработчики поиска клубов"""

    @bot.message_handler(func=lambda message: message.text == "🔍 Найти клубы")
    def search_clubs(message):
        """Показывает меню поиска клубов"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("🔍 По тегу", callback_data="search_by_tag")
        btn2 = types.InlineKeyboardButton("📍 По локации", callback_data="search_by_location")
        btn3 = types.InlineKeyboardButton("📋 Все клубы", callback_data="search_all")
        btn4 = types.InlineKeyboardButton("🎲 Случайный клуб", callback_data="search_random")
        markup.add(btn1, btn2, btn3, btn4)

        bot.send_message(message.chat.id, "Как хочешь искать клубы?", reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == "🎯 Мои клубы")
    def show_my_clubs(message):
        """Показывает клубы пользователя"""
        bot.send_message(message.chat.id, "Вот клубы в которых ты состоишь")

    def send_clubs_list(chat_id, clubs, title):
        """Отправляет список клубов пользователю"""
        bot.send_message(chat_id, "Список клубов по теме")

    def show_club_details(chat_id, club_id):
        """Показывает детальную информацию о клубе"""
        bot.send_message(chat_id, "Детали клуба")

    def join_club(user_id, chat_id, club_id):
        """Добавляет пользователя в клуб"""
        bot.send_message(chat_id, "Ты вступил в клуб")

    # Экспортируем функции для callback обработчика
    return {
        'send_clubs_list': send_clubs_list,
        'show_club_details': show_club_details,
        'join_club': join_club
    }

