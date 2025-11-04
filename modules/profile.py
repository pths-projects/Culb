"""
МОДУЛЬ РАБОТЫ С ПРОФИЛЕМ ПОЛЬЗОВАТЕЛЯ
Просмотр и редактирование профиля
"""

from telebot import types
from shared_functions import show_main_menu

def register_profile_handlers(bot, user_states):
    """Регистрирует обработчики профиля"""

    @bot.message_handler(func=lambda message: message.text == "👤 Мой профиль")
    def show_profile(message):
        """Показывает профиль пользователя"""
        response = "👤 Твой профиль:\n\n"
        response += "Имя: Человек\n"
        response += "Локация: Москва\n"
        response += "Интересы: программирование, музыка\n\n"
        response += "📊 Статистика:\n"
        response += "• Создано клубов: 2\n"
        response += "• Участвую в клубах: 3\n"

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
            show_main_menu(bot, message.chat.id, "Человек")
            return
        elif choice == "✏️ Изменить имя":
            msg = bot.send_message(chat_id, "Введите новое имя:", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, process_new_name, user_id)
        elif choice == "📍 Изменить локацию":
            msg = bot.send_message(chat_id, "Введите новую локацию:", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, process_new_location, user_id)
        elif choice == "🎯 Изменить интересы":
            msg = bot.send_message(chat_id, "Введите новые интересы:", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, process_new_interests, user_id)

    def process_new_name(message, user_id):
        """Обрабатывает изменение имени"""
        new_name = message.text.strip()
        bot.send_message(message.chat.id, f"✅ Имя успешно изменено на {new_name}!")
        show_main_menu(bot, message.chat.id, new_name)

    def process_new_location(message, user_id):
        """Обрабатывает изменение локации"""
        new_location = message.text.strip()
        bot.send_message(message.chat.id, f"✅ Локация успешно изменена на {new_location}!")
        show_main_menu(bot, message.chat.id, "Человек")

    def process_new_interests(message, user_id):
        """Обрабатывает изменение интересов"""
        new_interests = message.text.strip()
        bot.send_message(message.chat.id, f"✅ Интересы успешно обновлены!")
        show_main_menu(bot, message.chat.id, "Человек")

    return {
        'start_edit_profile': start_edit_profile
    }