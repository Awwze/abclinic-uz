import logging
import os
import time
from dotenv import load_dotenv
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

LANGUAGE, MENU, BOOK_APPOINTMENT, GET_NAME, GET_DATE_TIME, GET_PROBLEM, GET_PREFERRED_CONTACT, GET_PHONE, VACANCIES, STAFF, ABOUT_US, CONTACTS, FEEDBACK = range(13)

API_KEY = os.getenv('API_KEY')

user_data = {}

languages = ["🇺🇿 Узбекский", "🇷🇺 Русский", "🇬🇧 Английский"]
lang_dict = {"🇺🇿 Узбекский": "uz", "🇷🇺 Русский": "ru", "🇬🇧 Английский": "en"}

texts = {
    "start": {
        "uz": "Iltimos, tilni tanlang:",
        "ru": "Пожалуйста, выберите язык:",
        "en": "Please choose a language:"
    },
    "main_menu": {
        "uz": "Asosiy menyu:",
        "ru": "Главное меню:",
        "en": "Main menu:"
    },
    "book_appointment": {
        "uz": "Ismingizni kiriting:",
        "ru": "Введите ваше имя:",
        "en": "Enter your name:"
    },
    "enter_date_time": {
        "uz": "Qabul sanasi va vaqtini kiriting (masalan, 20-06-2024 15.00):",
        "ru": "Введите дату и время приёма (например, 20-06-2024 15.00):",
        "en": "Enter the appointment date and time (e.g., 20-06-2024 15.00):"
    },
    "enter_problem": {
        "uz": "Biz qanday yordam bera olamiz? (muammoingizni tavsiflang):",
        "ru": "Чем мы можем помочь? (опишите свою проблему):",
        "en": "How can we help? (describe your problem):"
    },
    "preferred_contact": {
        "uz": "Aloqa qilish usulini tanlang (SMS, TG, telefon orqali):",
        "ru": "Выберите предпочитаемый способ связи (SMS, TG, по телефону):",
        "en": "Choose preferred contact method (SMS, TG, phone):"
    },
    "enter_phone": {
        "uz": "Iltimos, telefon raqamingizni yuboring.",
        "ru": "Пожалуйста, отправьте ваш номер телефона.",
        "en": "Please send your phone number."
    },
    "thank_you": {
        "uz": "Rahmat! Sizning yozilishingiz qabul qilindi.",
        "ru": "Спасибо! Ваша запись принята.",
        "en": "Thank you! Your appointment is accepted."
    },
    "choose_option": {
        "uz": "Iltimos, menyu bandlaridan birini tanlang.",
        "ru": "Пожалуйста, выберите один из пунктов меню.",
        "en": "Please choose one of the menu items."
    },
    "vacancies": {
        "uz": "Bo'sh ish o'rinlari: \n\nNaši vakansii:\n«Otryad čistoty»\nAdministrator\nKoordinator lečeniya\nDetskiy stomatolog\nMenedžer\nFotograf",
        "ru": "Вакансии: \n\nНаши вакансии:\n«Отряд чистоты»\nАдминистратор\nКоординатор лечения\nДетский стоматолог\nМенеджер\nФотограф",
        "en": "Vacancies: \n\nOur vacancies:\n«Sanitation Team»\nAdministrator\nTreatment Coordinator\nPediatric Dentist\nManager\nPhotographer"
    },
    "staff": {
        "uz": "Bizning xodimlar: https://telegra.ph/Abclinic-06-19",
        "ru": "Наши сотрудники: https://telegra.ph/Abclinic-06-19",
        "en": "Our staff: https://telegra.ph/Abclinic-06-19"
    },
    "services": {
        "uz": "Narxlar va xizmatlar: https://telegra.ph/Abclinic-PRICE-LIST-06-19",
        "ru": "Прайсы и услуги: https://telegra.ph/Abclinic-PRICE-LIST-06-19",
        "en": "Prices and services: https://telegra.ph/Abclinic-PRICE-LIST-06-19"
    },
    "about_us": {
        "uz": "Biz haqimizda: (матнини ўзгартирасиз)",
        "ru": "О нас: (текст будет добавлен позже)",
        "en": "About Us: (text will be added later)"
    },
    "contacts": {
        "uz": "Kontaktlar:\nTelefon raqam: +998 95 122 88 55\nGeolokatsiya: https://clck.ru/3BRc5z\nBiz ijtimoiy tarmoqlarda:\nInstagram: https://www.instagram.com/abclinic.uz\nTelegram аккаунт: https://t.me/abclinic_uz",
        "ru": "Контакты:\nНомер телефона: +998 95 122 88 55\nГеолокация: https://clck.ru/3BRc5z\nМы в соц. сетях:\nInstagram: https://www.instagram.com/abclinic.uz\nTelegram аккаунт: https://t.me/abclinic_uz",
        "en": "Contacts:\nPhone number: +998 95 122 88 55\nGeolocation: https://clck.ru/3BRc5z\nWe are on social networks:\nInstagram: https://www.instagram.com/abclinic.uz\nTelegram account: https://t.me/abclinic_uz"
    },
    "goodbye": {
        "uz": "Xayr! Yana ko'rishguncha.",
        "ru": "До свидания! Надеемся увидеть вас снова.",
        "en": "Goodbye! Hope to see you again."
    },
    "feedback": {
        "uz": "Iltimos, o'z fikringizni va mulohazalaringizni yozing:",
        "ru": "Пожалуйста, напишите ваши пожелания и отзывы:",
        "en": "Please write your feedback and reviews:"
    }
}

# Главные меню
main_menu = {
    "uz": ["📅 royhatga quyish", "📋 Bo'sh ish o'rinlari", "👥 Bizning xodimlar", "📄 Narxlar va xizmatlar", "ℹ️ Biz haqimizda", "📞 Kontaktlar", "✍️ Fikringizni bildiring"],
    "ru": ["📅 Запись", "📋 Вакансии", "👥 Наши сотрудники", "📄 Прайсы и услуги", "ℹ️ О нас", "📞 Контакты", "✍️ Пожелания и отзывы"],
    "en": ["📅 Appointment", "📋 Vacancies", "👥 Our staff", "📄 Prices and services", "ℹ️ About Us", "📞 Contacts", "✍️ Feedback and Reviews"]
}

admin_chat_id = -4218562711

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [languages]
    await update.message.reply_text(
        texts['start']['ru'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return LANGUAGE

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_data[user_id] = {'lang': lang_dict[update.message.text]}
    lang = user_data[user_id]['lang']
    await update.message.reply_text(
        texts['start'][lang],
        reply_markup=ReplyKeyboardRemove()
    )
    return await show_menu(update, context)


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    lang = user_data[user_id]['lang']

    if update.message:
        buttons = [
            [KeyboardButton("📅 Запись"), KeyboardButton("📄 Прайсы и услуги")],
            [KeyboardButton("📞 Контакты"), KeyboardButton("ℹ️ О нас")],
            [KeyboardButton("👥 Наши сотрудники"), KeyboardButton("📋 Вакансии")],
            [KeyboardButton("✍️ Пожелания и отзывы")]
        ]
        
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        
        await update.message.reply_text(
            texts['main_menu'][lang],
            reply_markup=reply_markup
        )
    
    return MENU

async def menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    text = update.message.text
    lang = user_data[user_id]['lang']

    if text == "📅 Запись":
        await update.message.reply_text(texts['book_appointment'][lang], reply_markup=ReplyKeyboardRemove())
        return GET_NAME
    elif text == "📄 Прайсы и услуги":
        await update.message.reply_text(texts['services'][lang], reply_markup=ReplyKeyboardRemove())
        return await show_menu(update, context)
    elif text == "📞 Контакты":
        await update.message.reply_text(texts['contacts'][lang], reply_markup=ReplyKeyboardRemove())
        return await show_menu(update, context)
    elif text == "ℹ️ О нас":
        await update.message.reply_text(texts['about_us'][lang], reply_markup=ReplyKeyboardRemove())
        return await show_menu(update, context)
    elif text == "👥 Наши сотрудники":
        await update.message.reply_text(texts['staff'][lang], reply_markup=ReplyKeyboardRemove())
        return await show_menu(update, context)
    elif text == "📋 Вакансии":
        await update.message.reply_text(texts['vacancies'][lang], reply_markup=ReplyKeyboardRemove())
        return await show_menu(update, context)
    elif text == "✍️ Пожелания и отзывы":
        await update.message.reply_text(texts['feedback'][lang], reply_markup=ReplyKeyboardRemove())
        return FEEDBACK
    else:
        await update.message.reply_text(texts['choose_option'][lang], reply_markup=ReplyKeyboardRemove())
        return MENU

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_data[user_id]['name'] = update.message.text
    lang = user_data[user_id]['lang']
    await update.message.reply_text(texts['enter_date_time'][lang])
    return GET_DATE_TIME

async def get_date_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_data[user_id]['date_time'] = update.message.text
    lang = user_data[user_id]['lang']
    await update.message.reply_text(texts['enter_problem'][lang])
    return GET_PROBLEM

async def get_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_data[user_id]['problem'] = update.message.text
    lang = user_data[user_id]['lang']
    reply_keyboard = [["SMS", "TG", "по телефону"]]
    await update.message.reply_text(
        texts['preferred_contact'][lang],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return GET_PREFERRED_CONTACT

async def get_preferred_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_data[user_id]['contact'] = update.message.text
    lang = user_data[user_id]['lang']
    await update.message.reply_text(
        texts['enter_phone'][lang],
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📞 Отправить номер телефона", request_contact=True)]], one_time_keyboard=True, resize_keyboard=True)
    )
    return GET_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_data[user_id]['phone'] = update.message.contact.phone_number
    lang = user_data[user_id]['lang']
    user_info = user_data[user_id]
    user_name = update.message.from_user.username if update.message.from_user.username else "No username"
    
    await update.message.reply_text(
        texts['thank_you'][lang],
        reply_markup=ReplyKeyboardRemove()
    )

    await context.bot.send_message(
        chat_id=admin_chat_id,
        text=f"Новая запись от @{user_name}:\nИмя: {user_info['name']}\nДата и время: {user_info['date_time']}\nПроблема: {user_info['problem']}\nСпособ связи: {user_info['contact']}\nТелефон: {user_info['phone']}"
    )
    
    return await show_menu(update, context)

async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    lang = user_data[user_id]['lang']
    feedback = update.message.text
    user_name = update.message.from_user.username if update.message.from_user.username else "No username"

    await context.bot.send_message(
        chat_id=admin_chat_id,
        text=f"Новый отзыв и пожелание от @{user_name}:\n{feedback}"
    )

    await update.message.reply_text(texts['thank_you'][lang], reply_markup=ReplyKeyboardRemove())
    return await show_menu(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    lang = user_data.get(user_id, {}).get('lang', 'ru')
    await update.message.reply_text(texts['goodbye'][lang], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def command_appointment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await menu_selection(update, context)

async def command_vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await menu_selection(update, context)

async def command_staff(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await menu_selection(update, context)

async def command_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await menu_selection(update, context)

async def command_about_us(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await menu_selection(update, context)

async def command_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await menu_selection(update, context)

async def command_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await menu_selection(update, context)

def run_bot() -> None:
    application = Application.builder().token(API_KEY).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_language)],
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_selection)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_DATE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date_time)],
            GET_PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_problem)],
            GET_PREFERRED_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_preferred_contact)],
            GET_PHONE: [MessageHandler(filters.CONTACT, get_phone)],
            FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.add_handler(CommandHandler('appointment', command_appointment))
    application.add_handler(CommandHandler('vacancies', command_vacancies))
    application.add_handler(CommandHandler('staff', command_staff))
    application.add_handler(CommandHandler('services', command_services))
    application.add_handler(CommandHandler('about_us', command_about_us))
    application.add_handler(CommandHandler('contacts', command_contacts))
    application.add_handler(CommandHandler('feedback', command_feedback))

    application.run_polling()

if __name__ == '__main__':
    while True:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            run_bot()
        except Exception as e:
            logging.error(f"Bot crashed with error: {e}")
