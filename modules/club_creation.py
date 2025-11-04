"""
МОДУЛЬ СОЗДАНИЯ НОВЫХ КЛУБОВ
Многошаговый процесс создания клуба
"""

from telebot import types
from shared_functions import validate_name, validate_description, validate_telegram_link


def register_creation_handlers(bot, user_states, show_main_menu_func):
    """Регистрирует обработчики создания клубов"""

    @bot.message_handler(func=lambda message: message.text == "➕ Создать клуб")
    def start_create_club(message):
        """Начинает процесс создания клуба"""
        msg = bot.send_message(message.chat.id, "Ты начал создавать клуб. Как он будет называться?")
        user_states[message.from_user.id] = {'step': 'creating_club', 'data': {}}
        bot.register_next_step_handler(msg, process_club_name)

    def process_club_name(message):
        """Обрабатывает ввод названия клуба"""
        user_id = message.from_user.id
        club_name = message.text.strip()

        if user_id in user_states:
            user_states[user_id]['data']['name'] = club_name
            msg = bot.send_message(message.chat.id, "Принято! Теперь опиши деятельность клуба:")
            bot.register_next_step_handler(msg, process_club_description)

    def process_club_description(message):
        """Обрабатывает ввод описания клуба"""
        user_id = message.from_user.id
        description = message.text.strip()

        if user_id in user_states:
            user_states[user_id]['data']['description'] = description
            club_name = user_states[user_id]['data']['name']
            msg = bot.send_message(message.chat.id,
                                   f"Клуб '{club_name}' с описанием '{description}'! Теперь укажи теги:")
            bot.register_next_step_handler(msg, process_club_tags)

    def process_club_tags(message):
        """Обрабатывает ввод тегов клуба"""
        user_id = message.from_user.id
        tags = message.text.strip()

        if user_id in user_states:
            user_states[user_id]['data']['tags'] = tags
            msg = bot.send_message(message.chat.id, f"Теги '{tags}' приняты! Укажи город:")
            bot.register_next_step_handler(msg, process_club_location)

    def process_club_location(message):
        """Обрабатывает ввод локации клуба"""
        user_id = message.from_user.id
        location = message.text.strip()

        if user_id in user_states:
            user_states[user_id]['data']['location'] = location
            msg = bot.send_message(message.chat.id, f"Город '{location}' принят! Пришли ссылку на чат:")
            bot.register_next_step_handler(msg, process_club_chat_link)

    def process_club_chat_link(message):
        """Обрабатывает ввод ссылки на чат и создает клуб"""
        user_id = message.from_user.id
        chat_link = message.text.strip()

        if not validate_telegram_link(chat_link):
            msg = bot.send_message(message.chat.id,
                                   "Это не похоже на ссылку Telegram. Пришли корректную ссылку (начинается с https://t.me/):")
            bot.register_next_step_handler(msg, process_club_chat_link)
            return

        if user_id in user_states:
            club_data = user_states[user_id]['data']

            # Создаем клуб
            bot.send_message(message.chat.id, f"Создан клуб: '{club_data['name']}'")

            # Добавляем владельца в участники
            bot.send_message(message.chat.id, "Владелец добавлен в участники клуба")

            # Очищаем состояние
            del user_states[user_id]

            # Показываем главное меню
            show_main_menu_func(bot, message.chat.id, "Человек")

    return {}