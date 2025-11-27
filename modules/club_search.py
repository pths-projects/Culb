"""
МОДУЛЬ ПОИСКА И ПРОСМОТРА КЛУБОВ
Поиск клубов по тегам, локации, просмотр деталей клуба
"""

from telebot import types
from repositories import user_repo, club_repo, member_repo
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
        user_id = message.from_user.id
        user_clubs = member_repo.get_user_clubs(user_id)
        owned_clubs = club_repo.get_clubs_by_owner(user_id)

        if not user_clubs and not owned_clubs:
            bot.send_message(message.chat.id, "Ты пока не состоишь ни в одном клубе. Найди клубы по интересам!")
            return

        response = "🎯 Твои клубы:\n\n"

        if owned_clubs:
            response += "🏆 Клубы, которые ты создал:\n"
            for club in owned_clubs:
                response += f"• {club.name} (ID: {club.club_id})\n"
            response += "\n"

        if user_clubs:
            response += "👥 Клубы, в которых ты состоишь:\n"
            for club in user_clubs:
                response += f"• {club.name} (ID: {club.club_id})\n"

        bot.send_message(message.chat.id, response)

    def send_clubs_list(chat_id, clubs, title):
        """Отправляет список клубов пользователю"""
        if not clubs:
            bot.send_message(chat_id, "По вашему запросу ничего не найдено 😔")
            return

        response = f"{title}\n\n"

        for i, club in enumerate(clubs[:5], 1):
            response += f"{i}. {club.name}\n"
            response += f"   📍 {club.location}\n"
            response += f"   🏷️ {club.tags}\n"
            response += f"   ID: {club.club_id}\n\n"

        markup = types.InlineKeyboardMarkup()
        for club in clubs[:3]:
            btn = types.InlineKeyboardButton(f"🔍 {club.name}", callback_data=f"club_details_{club.club_id}")
            markup.add(btn)

        bot.send_message(chat_id, response, reply_markup=markup)

    def show_club_details(chat_id, club_id):
        """Показывает детальную информацию о клубе"""
        club = club_repo.get_club_by_id(club_id)
        if not club:
            bot.send_message(chat_id, "Клуб не найден")
            return

        response = f"🏛️ {club.name}\n\n"
        response += f"📝 {club.description}\n\n"
        response += f"📍 Локация: {club.location}\n"
        response += f"🏷️ Теги: {club.tags}\n"

        members = member_repo.get_club_members(club_id)
        response += f"👥 Участников: {len(members)}\n\n"

        markup = types.InlineKeyboardMarkup()
        join_btn = types.InlineKeyboardButton("✅ Вступить в клуб", callback_data=f"join_{club_id}")
        chat_btn = types.InlineKeyboardButton("💬 Перейти в чат", url=club.chat_link)
        markup.add(join_btn, chat_btn)

        bot.send_message(chat_id, response, reply_markup=markup)

    def join_club(user_id, chat_id, club_id):
        """Добавляет пользователя в клуб"""
        if member_repo.is_user_club_member(user_id, club_id):
            bot.send_message(chat_id, "Ты уже состоишь в этом клубе!")
            user = user_repo.get_user_by_tg_id(user_id)
            show_main_menu(bot, chat_id, user.name)
            return

        success = member_repo.add_member_to_club(user_id, club_id)
        if success:
            club = club_repo.get_club_by_id(club_id)
            bot.send_message(chat_id, f"🎉 Поздравляю! Ты вступил в клуб '{club.name}'!")
        else:
            bot.send_message(chat_id, "Не удалось вступить в клуб. Попробуй позже.")

        user = user_repo.get_user_by_tg_id(user_id)
        show_main_menu(bot, chat_id, user.name)

    # Экспортируем функции для callback обработчика
    return {
        'send_clubs_list': send_clubs_list,
        'show_club_details': show_club_details,
        'join_club': join_club
    }