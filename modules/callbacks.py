"""
МОДУЛЬ ОБРАБОТКИ INLINE-КНОПОК
Обработка всех callback_query от инлайн-кнопок
"""

from telebot import types
from shared_functions import show_main_menu

def register_callback_handlers(bot, user_states, search_handlers, profile_handlers):
    """Регистрирует обработчики callback_query"""

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callbacks(call):
        """Основной обработчик inline-кнопок"""
        user_id = call.from_user.id
        chat_id = call.message.chat.id

        if call.data == "search_all":
            # Поиск всех клубов
            search_handlers['send_clubs_list'](chat_id, [], "Все активные клубы:")
            show_main_menu(bot, chat_id, "Человек")

        elif call.data == "search_by_tag":
            # Поиск по тегу
            msg = bot.send_message(chat_id, "Введите тег для поиска (например: #игры, #спорт, #it):")
            bot.register_next_step_handler(msg, process_tag_search)

        elif call.data == "search_by_location":
            # Поиск по локации
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(types.KeyboardButton("📍 Использовать Москву"))
            markup.add(types.KeyboardButton("❌ Отмена"))

            msg = bot.send_message(chat_id, "Введите город для поиска:", reply_markup=markup)
            bot.register_next_step_handler(msg, process_location_search, "Москва")

        elif call.data.startswith("join_"):
            # Вступление в клуб
            search_handlers['join_club'](user_id, chat_id, 1)
            show_main_menu(bot, chat_id, "Человек")

        elif call.data.startswith("club_details_"):
            # Просмотр деталей клуба
            search_handlers['show_club_details'](chat_id, 1)
            show_main_menu(bot, chat_id, "Человек")

        elif call.data == "edit_profile":
            # Редактирование профиля
            profile_handlers['start_edit_profile'](chat_id, user_id)

    def process_tag_search(message):
        """Обрабатывает поиск по тегу"""
        tag = message.text.strip()
        search_handlers['send_clubs_list'](message.chat.id, [], f"Результаты поиска по тегу '{tag}':")
        show_main_menu(bot, message.chat.id, "Человек")

    def process_location_search(message, default_location):
        """Обрабатывает поиск по локации"""
        location = message.text.strip()

        if location == "📍 Использовать Москву":
            location = "Москва"
        elif location == "❌ Отмена":
            bot.send_message(message.chat.id, "Поиск отменен", reply_markup=types.ReplyKeyboardRemove())
            show_main_menu(bot, message.chat.id, "Человек")
            return

        search_handlers['send_clubs_list'](message.chat.id, [], f"Результаты поиска по локации '{location}':")
        show_main_menu(bot, message.chat.id, "Человек")

    return {}