"""
МОДУЛЬ СОЗДАНИЯ НОВЫХ КЛУБОВ
Многошаговый процесс создания клуба
"""

from telebot import types
import database
from shared_functions import validate_name, validate_description, validate_telegram_link


def register_creation_handlers(bot, user_states, show_main_menu_func):
    """Регистрирует обработчики создания клубов"""

    @bot.message_handler(func=lambda message: message.text == "➕ Создать клуб")
    def start_create_club(message):
        """Начинает процесс создания клуба"""
        user_id = message.from_user.id
        user = database.get_user_by_tg_id(user_id)

        if not user or not user['location']:
            # Если нет локации, запрашиваем ее
            msg = bot.send_message(message.chat.id, "📝 Для создания клуба нужна твоя локация. Введи свой город:")
            bot.register_next_step_handler(msg, process_immediate_location)
            return

        # Если все данные есть, начинаем создание клуба
        msg = bot.send_message(message.chat.id, "Отлично! Давай создадим твой клуб. Как он будет называться?")
        user_states[user_id] = {'step': 'creating_club', 'data': {}}
        bot.register_next_step_handler(msg, process_club_name)

    def process_immediate_location(message):
        """Обрабатывает немедленный ввод локации"""
        location = message.text.strip()
        user_id = message.from_user.id

        if database.update_user(user_id, location=location):
            bot.send_message(message.chat.id, "✅ Локация сохранена! Теперь можно создать клуб.")
            start_create_club(message)  # Возвращаем к созданию клуба
        else:
            bot.send_message(message.chat.id, "❌ Ошибка. Попробуй еще раз /start")

    def process_club_name(message):
        """Обрабатывает ввод названия клуба"""
        user_id = message.from_user.id
        club_name = message.text.strip()

        if not validate_name(club_name):
            msg = bot.send_message(message.chat.id,
                                   "Название слишком короткое. Введите название минимум из 3 символов:")
            bot.register_next_step_handler(msg, process_club_name)
            return

        if user_id in user_states:
            user_states[user_id]['data']['name'] = club_name
            msg = bot.send_message(message.chat.id, "Отличное название! Теперь опиши, чем будет заниматься твой клуб:")
            bot.register_next_step_handler(msg, process_club_description)

    def process_club_description(message):
        """Обрабатывает ввод описания клуба"""
        user_id = message.from_user.id
        description = message.text.strip()

        if not validate_description(description):
            msg = bot.send_message(message.chat.id,
                                   "Описание слишком короткое. Расскажи подробнее (минимум 10 символов):")
            bot.register_next_step_handler(msg, process_club_description)
            return

        if user_id in user_states:
            user_states[user_id]['data']['description'] = description
            msg = bot.send_message(message.chat.id,
                                   "Теперь укажи теги для твоего клуба (через запятую). Например: #игры, #общение, #it")
            bot.register_next_step_handler(msg, process_club_tags)

    def process_club_tags(message):
        """Обрабатывает ввод тегов клуба"""
        user_id = message.from_user.id
        tags = message.text.strip()

        if user_id in user_states:
            user_states[user_id]['data']['tags'] = tags
            user = database.get_user_by_tg_id(user_id)
            default_location = user['location'] if user['location'] else 'default'

            msg = bot.send_message(message.chat.id, f"Где будут проходить встречи? (по умолчанию: {default_location})")
            bot.register_next_step_handler(msg, process_club_location)

    def process_club_location(message):
        """Обрабатывает ввод локации клуба"""
        user_id = message.from_user.id
        location = message.text.strip()

        if user_id in user_states:
            # Если пользователь просто нажал Enter или ввёл пустую строку,
            # используем локацию пользователя по умолчанию
            if not location:
                user = database.get_user_by_tg_id(user_id)
                location = user['location'] if user and user['location'] else 'Не указана'

            user_states[user_id]['data']['location'] = location

            msg = bot.send_message(message.chat.id, "Последний шаг! Пришли ссылку на Telegram-чат твоего клуба:")
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

            # Создаем клуб в БД
            club_id = database.create_club(
                owner_id=user_id,
                name=club_data['name'],
                description=club_data['description'],
                tags=club_data['tags'],
                location=club_data['location'] if club_data['location'] else 'Не указана',
                chat_link=chat_link
            )

            # Добавляем создателя в участники
            database.add_member_to_club(user_id, club_id)

            # Очищаем состояние
            del user_states[user_id]

            # Показываем главное меню
            user = database.get_user_by_tg_id(user_id)
            show_main_menu_func(bot, message.chat.id, user['name'])
            bot.send_message(message.chat.id, f"🎉 Поздравляю! Твой клуб '{club_data['name']}' создан!")

    return {}