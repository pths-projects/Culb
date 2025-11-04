"""
МОДУЛЬ РАБОТЫ С ПРОФИЛЕМ ПОЛЬЗОВАТЕЛЯ
Просмотр и редактирование профиля
"""

from telebot import types
import database
from shared_functions import show_main_menu

def register_profile_handlers(bot, user_states):
    """Регистрирует обработчики профиля"""

    @bot.message_handler(func=lambda message: message.text == "👤 Мой профиль")
    def show_profile(message):
        """Показывает профиль пользователя"""
        user_id = message.from_user.id
        user = database.get_user_by_tg_id(user_id)

        if not user:
            bot.send_message(message.chat.id, "Сначала зарегистрируйся через /start")
            return

        # ПРАВИЛЬНОЕ обращение к sqlite3.Row объекту
        response = f"👤 Твой профиль:\n\n"
        response += f"Имя: {user['name']}\n"
        response += f"Локация: {user['location'] if user['location'] else 'Не указана'}\n"
        response += f"Интересы: {user['interests'] if user['interests'] else 'Не указаны'}\n\n"

        # Статистика
        user_clubs = database.get_user_clubs(user_id)
        owned_clubs = database.get_clubs_by_owner(user_id)

        response += f"📊 Статистика:\n"
        response += f"• Создано клубов: {len(owned_clubs)}\n"
        response += f"• Участвую в клубах: {len(user_clubs)}\n"

        markup = types.InlineKeyboardMarkup()
        btn_edit = types.InlineKeyboardButton("✏️ Редактировать профиль", callback_data="edit_profile")
        markup.add(btn_edit)

        bot.send_message(message.chat.id, response, reply_markup=markup)

    def start_edit_profile(chat_id, user_id):
        """Начинает процесс редактирования профиля"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn_name = types.KeyboardButton("✏️ Изменить имя")
        btn_location = types.KeyboardButton("📍 Изменить локацию")
        btn_interests = types.KeyboardButton("🎯 Изменить интересы")
        btn_cancel = types.KeyboardButton("❌ Отмена")
        markup.add(btn_name, btn_location, btn_interests, btn_cancel)

        msg = bot.send_message(chat_id, "Что хочешь изменить в профиле?", reply_markup=markup)
        bot.register_next_step_handler(msg, process_edit_choice, user_id)

    def process_edit_choice(message, user_id):
        """Обрабатывает выбор поля для редактирования"""
        choice = message.text
        chat_id = message.chat.id

        if choice == "❌ Отмена":
            bot.send_message(chat_id, "Редактирование отменено", reply_markup=types.ReplyKeyboardRemove())
            user = database.get_user_by_tg_id(user_id)
            show_main_menu(bot, message.chat.id, user['name'])
            return
        elif choice == "✏️ Изменить имя":
            msg = bot.send_message(chat_id, "Введите новое имя:", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, process_new_name, user_id)
        elif choice == "📍 Изменить локацию":
            msg = bot.send_message(chat_id, "Введите новую локацию:", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, process_new_location, user_id)
        elif choice == "🎯 Изменить интересы":
            msg = bot.send_message(chat_id, "Введите новые интересы (через запятую):",
                                   reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, process_new_interests, user_id)

    def process_new_name(message, user_id):
        """Обрабатывает изменение имени"""
        new_name = message.text.strip()
        if database.update_user(user_id, name=new_name):
            bot.send_message(message.chat.id, f"✅ Имя успешно изменено на {new_name}!")

        else:
            bot.send_message(message.chat.id, "❌ Не удалось изменить имя")

        user = database.get_user_by_tg_id(user_id)
        show_main_menu(bot, message.chat.id, user['name'])

    def process_new_location(message, user_id):
        """Обрабатывает изменение локации"""
        new_location = message.text.strip()
        if database.update_user(user_id, location=new_location):
            bot.send_message(message.chat.id, f"✅ Локация успешно изменена на {new_location}!")
        else:
            bot.send_message(message.chat.id, "❌ Не удалось изменить локацию")
        user = database.get_user_by_tg_id(user_id)
        show_main_menu(bot, message.chat.id, user['name'])

    def process_new_interests(message, user_id):
        """Обрабатывает изменение интересов"""
        new_interests = message.text.strip()
        if database.update_user(user_id, interests=new_interests):
            bot.send_message(message.chat.id, f"✅ Интересы успешно обновлены!")
        else:
            bot.send_message(message.chat.id, "❌ Не удалось изменить интересы")
        user = database.get_user_by_tg_id(user_id)
        show_main_menu(bot, message.chat.id, user['name'])

    return {
        'start_edit_profile': start_edit_profile
    }