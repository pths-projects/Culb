"""
МОДУЛЬ ОБРАБОТКИ INLINE-КНОПОК
Обработка всех callback_query от инлайн-кнопок
"""

from telebot import types
from repositories import user_repo, club_repo
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
            clubs = club_repo.get_all_active_clubs(limit=10)
            search_handlers['send_clubs_list'](chat_id, clubs, "Все активные клубы:")

            user = user_repo.get_user_by_tg_id(user_id)
            show_main_menu(bot, chat_id, user.name)

        elif call.data == "search_random":
            # Случайный клуб (балванка)
            clubs = club_repo.get_all_active_clubs(limit=1)
            search_handlers['send_clubs_list'](chat_id, clubs, "Последний созданный клуб:")

            user = user_repo.get_user_by_tg_id(user_id)
            show_main_menu(bot, chat_id, user.name)

        elif call.data == "search_by_tag":
            # Поиск по тегу
            msg = bot.send_message(chat_id, "Введите тег для поиска (например: #игры, #спорт, #it):")
            bot.register_next_step_handler(msg, process_tag_search)

        elif call.data == "search_by_location":
            # Поиск по локации
            user = user_repo.get_user_by_tg_id(user_id)
            default_location = user.location if user and user.location else ''
            prompt = "Введите локацию для поиска:"
            if default_location:
                prompt += f"\n(или нажмите '📍 Использовать мою локацию' - {default_location})"

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            if default_location:
                markup.add(types.KeyboardButton("📍 Использовать мою локацию"))
            markup.add(types.KeyboardButton("❌ Отмена"))

            msg = bot.send_message(chat_id, prompt, reply_markup=markup)
            bot.register_next_step_handler(msg, process_location_search, default_location)

        elif call.data.startswith("join_"):
            # Вступление в клуб
            club_id = int(call.data.split("_")[1])
            search_handlers['join_club'](user_id, chat_id, club_id)

            user = user_repo.get_user_by_tg_id(user_id)
            show_main_menu(bot, chat_id, user.name)

        elif call.data.startswith("club_details_"):
            # Просмотр деталей клуба
            club_id = int(call.data.split("_")[2])
            search_handlers['show_club_details'](chat_id, club_id)

            user = user_repo.get_user_by_tg_id(user_id)
            show_main_menu(bot, chat_id, user.name)

        elif call.data == "edit_profile":
            # Редактирование профиля
            profile_handlers['start_edit_profile'](chat_id, user_id)

    def process_tag_search(message):
        """Обрабатывает поиск по тегу"""
        tag = message.text.strip()
        clubs = club_repo.search_clubs_by_tag(tag)
        search_handlers['send_clubs_list'](message.chat.id, clubs, f"Результаты поиска по тегу '{tag}':")

        user = user_repo.get_user_by_tg_id(message.from_user.id)
        show_main_menu(bot, message.chat.id, user.name)

    def process_location_search(message, default_location):
        """Обрабатывает поиск по локации"""
        location = message.text.strip()

        if location == "📍 Использовать мою локацию" and default_location:
            location = default_location
        elif location == "❌ Отмена":
            bot.send_message(message.chat.id, "Поиск отменен", reply_markup=types.ReplyKeyboardRemove())
            user = user_repo.get_user_by_tg_id(message.from_user.id)
            show_main_menu(bot, message.chat.id, user.name)
            return

        clubs = club_repo.search_clubs_by_location(location)
        search_handlers['send_clubs_list'](message.chat.id, clubs, f"Результаты поиска по локации '{location}':")

        user = user_repo.get_user_by_tg_id(message.from_user.id)
        show_main_menu(bot, message.chat.id, user.name)
    return {}