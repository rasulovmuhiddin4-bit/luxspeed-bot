import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, 
    InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Log konfiguratsiyasi
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
load_dotenv()

# Bot konfiguratsiyasi
BOT_TOKEN = "8144591571:AAFV2kUDW8ZXZ8clt1JLNHeeZ_bfycYbQ0Q"
ADMIN_ID = 8139728271
ADMIN_USERNAME = "@ALoqa_admin1985"

# Bot va Dispatcher yaratish
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Ma'lumotlar bazasi
users_db = {}
orders_db = {}

# Reply Keyboard yaratish funksiyalari
def get_main_menu_keyboard(language: str = 'uz'):
    """Asosiy menyu keyboard"""
    if language == 'uz':
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🚖 Taksi chaqirish"), KeyboardButton(text="📋 Mening buyurtmalarim")],
                [KeyboardButton(text="👤 Profil"), KeyboardButton(text="🌐 Tilni o'zgartirish")],
                [KeyboardButton(text="🆘 Yordam"), KeyboardButton(text="🔄 Rolni o'zgartirish")]
            ],
            resize_keyboard=True,
            input_field_placeholder="Quyidagi menyulardan birini tanlang..."
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🚖 Вызвать такси"), KeyboardButton(text="📋 Мои заказы")],
                [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🌐 Сменить язык")],
                [KeyboardButton(text="🆘 Помощь"), KeyboardButton(text="🔄 Сменить роль")]
            ],
            resize_keyboard=True,
            input_field_placeholder="Выберите один из пунктов меню..."
        )
    return keyboard

def get_driver_menu_keyboard(language: str = 'uz'):
    """Haydovchi menyusi"""
    if language == 'uz':
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="👥 Mijoz qidirish"), KeyboardButton(text="📊 Statistika")],
                [KeyboardButton(text="🚗 Mening mashinam"), KeyboardButton(text="💰 Balans")],
                [KeyboardButton(text="👤 Profil"), KeyboardButton(text="🌐 Tilni o'zgartirish")],
                [KeyboardButton(text="🆘 Yordam"), KeyboardButton(text="🔄 Rolni o'zgartirish")]
            ],
            resize_keyboard=True,
            input_field_placeholder="Haydovchi menyusi..."
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="👥 Поиск клиентов"), KeyboardButton(text="📊 Статистика")],
                [KeyboardButton(text="🚗 Моя машина"), KeyboardButton(text="💰 Баланс")],
                [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="🌐 Сменить язык")],
                [KeyboardButton(text="🆘 Помощь"), KeyboardButton(text="🔄 Сменить роль")]
            ],
            resize_keyboard=True,
            input_field_placeholder="Меню водителя..."
        )
    return keyboard

def get_language_keyboard():
    """Til tanlash keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Tilni tanlang..."
    )
    return keyboard

def get_role_keyboard(language: str = 'uz'):
    """Rol tanlash keyboard"""
    if language == 'uz':
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🚕 Haydovchi"), KeyboardButton(text="👤 Mijoz")],
                [KeyboardButton(text="🔙 Orqaga")]
            ],
            resize_keyboard=True,
            input_field_placeholder="Rolni tanlang..."
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🚕 Водитель"), KeyboardButton(text="👤 Клиент")],
                [KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True,
            input_field_placeholder="Выберите роль..."
        )
    return keyboard

def get_back_keyboard(language: str = 'uz'):
    """Orqaga keyboard"""
    if language == 'uz':
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Orqaga")]],
            resize_keyboard=True
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🔙 Назад")]],
            resize_keyboard=True
        )
    return keyboard

# Start komandasi
@dp.message(Command("start"))
async def start_command(message: Message):
    user = message.from_user
    user_id = user.id
    
    # Foydalanuvchini bazaga qo'shish
    if user_id not in users_db:
        users_db[user_id] = {
            'first_name': user.first_name,
            'last_name': user.last_name or '',
            'username': user.username or '',
            'language': 'uz',
            'role': None,
            'phone': '',
            'registered_at': datetime.now().isoformat(),
            'status': 'active'
        }
    
    user_data = users_db[user_id]
    
    # Agar til tanlanmagan bo'lsa
    if user_data['language'] is None:
        await message.answer(
            "🇺🇿 Assalomu alaykum! Luxspeed botiga xush kelibsiz!\n"
            "🇷🇺 Здравствуйте! Добро пожаловать в бот Luxspeed!\n\n"
            "Iltimos, tilni tanlang / Пожалуйста, выберите язык:",
            reply_markup=get_language_keyboard()
        )
        return
    
    # Agar rol tanlanmagan bo'lsa
    if user_data['role'] is None:
        lang = user_data['language']
        if lang == 'uz':
            text = "🚕 Iltimos, rolizingizni tanlang:"
        else:
            text = "🚕 Пожалуйста, выберите вашу роль:"
        
        await message.answer(text, reply_markup=get_role_keyboard(lang))
        return
    
    # Agar hammasi tanlangan bo'lsa
    await show_main_menu(message, user_data)

# Asosiy menyuni ko'rsatish
async def show_main_menu(message: Message, user_data: dict):
    user_id = message.from_user.id
    language = user_data['language']
    role = user_data['role']
    
    if role == 'driver':
        # Haydovchi menyusi
        if language == 'uz':
            welcome_text = f"🚕 Haydovchi paneliga xush kelibsiz, {user_data['first_name']}!"
        else:
            welcome_text = f"🚕 Добро пожаловать в панель водителя, {user_data['first_name']}!"
        
        await message.answer(welcome_text, reply_markup=get_driver_menu_keyboard(language))
    else:
        # Mijoz menyusi
        if language == 'uz':
            welcome_text = f"👤 Mijoz paneliga xush kelibsiz, {user_data['first_name']}!"
        else:
            welcome_text = f"👤 Добро пожаловать в панель клиента, {user_data['first_name']}!"
        
        await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(language))

# Til tanlash handler
@dp.message(F.text.in_(["🇺🇿 O'zbekcha", "🇷🇺 Русский"]))
async def language_selection(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id)
    
    if not user_data:
        await start_command(message)
        return
    
    if message.text == "🇺🇿 O'zbekcha":
        user_data['language'] = 'uz'
        text = "🇺🇿 O'zbek tili tanlandi!\n\nIltimos, rolizingizni tanlang:"
    else:
        user_data['language'] = 'ru'
        text = "🇷🇺 Русский язык выбран!\n\nПожалуйста, выберите вашу роль:"
    
    await message.answer(text, reply_markup=get_role_keyboard(user_data['language']))

# Rol tanlash handler
@dp.message(F.text.in_(["🚕 Haydovchi", "👤 Mijoz", "🚕 Водитель", "👤 Клиент"]))
async def role_selection(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_data)
    
    if not user_data:
        await start_command(message)
        return
    
    language = user_data['language']
    
    if message.text in ["🚕 Haydovchi", "🚕 Водитель"]:
        user_data['role'] = 'driver'
        role_text_uz = "Haydovchi"
        role_text_ru = "Водитель"
    else:
        user_data['role'] = 'customer'
        role_text_uz = "Mijoz"
        role_text_ru = "Клиент"
    
    # WebApp URL
    web_app_url = f"https://luxspeed-taksi.netlify.app/?user_id={user_id}&role={user_data['role']}&lang={language}"
    
    if language == 'uz':
        success_text = f"✅ {role_text_uz} roli tanlandi!\n\n"
        success_text += "Quyidagi tugmani bosib to'liq interfeysga o'ting yoki pastdagi menyudan foydalaning:"
        btn_text = "🚀 To'liq Interfeysni Ochish"
    else:
        success_text = f"✅ Роль {role_text_ru} выбрана!\n\n"
        success_text += "Нажмите кнопку ниже для перехода в полный интерфейс или используйте меню:"
        btn_text = "🚀 Открыть Полный Интерфейс"
    
    # Inline keyboard WebApp uchun
    webapp_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=btn_text, web_app=WebAppInfo(url=web_app_url))]]
    )
    
    await message.answer(success_text, reply_markup=webapp_keyboard)
    
    # Asosiy menyuni ko'rsatish
    await show_main_menu(message, user_data)
    
    # Adminga xabar berish
    admin_text = (
        f"🔄 Rol tanlandi:\n"
        f"👤 Foydalanuvchi: {user_data['first_name']}\n"
        f"📱 Username: @{user_data['username'] or 'Yoq'}\n"
        f"🆔 ID: {user_id}\n"
        f"🎯 Rol: {role_text_uz}\n"
        f"🌐 Til: {language}\n"
        f"⏰ Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    try:
        await bot.send_message(ADMIN_ID, admin_text)
    except Exception as e:
        logger.error(f"Adminga xabar yuborishda xatolik: {e}")

# Orqaga tugmasi handler
@dp.message(F.text.in_(["🔙 Orqaga", "🔙 Назад"]))
async def back_handler(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id)
    
    if not user_data:
        await start_command(message)
        return
    
    await show_main_menu(message, user_data)

# Taksi chaqirish handler
@dp.message(F.text.in_(["🚖 Taksi chaqirish", "🚖 Вызвать такси"]))
async def order_taxi(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id)
    
    if not user_data or user_data['role'] != 'customer':
        await message.answer("❌ Siz mijoz emassiz!", reply_markup=get_main_menu_keyboard(user_data['language']))
        return
    
    language = user_data['language']
    web_app_url = f"https://luxspeed-taksi.netlify.app/?user_id={user_id}&role=customer&lang={language}"
    
    if language == 'uz':
        text = "🚖 Taksi chaqirish uchun to'liq interfeysga o'ting:"
        btn_text = "📍 Taksi Chaqirish"
    else:
        text = "🚖 Перейдите в полный интерфейс для вызова такси:"
        btn_text = "📍 Вызвать Такси"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=btn_text, web_app=WebAppInfo(url=web_app_url))]]
    )
    
    await message.answer(text, reply_markup=keyboard)

# Mijoz qidirish handler
@dp.message(F.text.in_(["👥 Mijoz qidirish", "👥 Поиск клиентов"]))
async def find_customer(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id)
    
    if not user_data or user_data['role'] != 'driver':
        await message.answer("❌ Siz haydovchi emassiz!", reply_markup=get_driver_menu_keyboard(user_data['language']))
        return
    
    language = user_data['language']
    web_app_url = f"https://luxspeed-taksi.netlify.app/?user_id={user_id}&role=driver&lang={language}"
    
    if language == 'uz':
        text = "👥 Mijozlarni qidirish uchun to'liq interfeysga o'ting:"
        btn_text = "🔍 Mijoz Qidirish"
    else:
        text = "👥 Перейдите в полный интерфейс для поиска клиентов:"
        btn_text = "🔍 Поиск Клиентов"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=btn_text, web_app=WebAppInfo(url=web_app_url))]]
    )
    
    await message.answer(text, reply_markup=keyboard)

# Profil handler
@dp.message(F.text.in_(["👤 Profil", "👤 Профиль"]))
async def show_profile(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id)
    
    if not user_data:
        await start_command(message)
        return
    
    language = user_data['language']
    role = user_data['role']
    
    if language == 'uz':
        profile_text = (
            f"👤 Sizning profilingiz:\n\n"
            f"🏷️ Ism: {user_data['first_name']} {user_data['last_name']}\n"
            f"📱 Username: @{user_data['username'] or 'Mavjud emas'}\n"
            f"🎯 Rol: {'Haydovchi' if role == 'driver' else 'Mijoz'}\n"
            f"🌐 Til: O'zbekcha\n"
            f"📅 Ro'yxatdan o'tgan: {user_data['registered_at'][:10]}\n"
            f"🆔 ID: {user_id}"
        )
    else:
        profile_text = (
            f"👤 Ваш профиль:\n\n"
            f"🏷️ Имя: {user_data['first_name']} {user_data['last_name']}\n"
            f"📱 Username: @{user_data['username'] or 'Нет'}\n"
            f"🎯 Роль: {'Водитель' if role == 'driver' else 'Клиент'}\n"
            f"🌐 Язык: Русский\n"
            f"📅 Зарегистрирован: {user_data['registered_at'][:10]}\n"
            f"🆔 ID: {user_id}"
        )
    
    await message.answer(profile_text)

# Tilni o'zgartirish handler
@dp.message(F.text.in_(["🌐 Tilni o'zgartirish", "🌐 Сменить язык"]))
async def change_language(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id)
    
    if not user_data:
        await start_command(message)
        return
    
    language = user_data['language']
    
    if language == 'uz':
        text = "🌐 Qaysi tilga o'zgartirmoqchisiz?"
    else:
        text = "🌐 На какой язык хотите поменять?"
    
    await message.answer(text, reply_markup=get_language_keyboard())

# Yordam handler
@dp.message(F.text.in_(["🆘 Yordam", "🆘 Помощь"]))
async def help_command(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id)
    
    if not user_data:
        await start_command(message)
        return
    
    language = user_data['language']
    
    if language == 'uz':
        help_text = (
            "🆘 Yordam markazi\n\n"
            "📞 Qo'llab-quvvatlash: @ALoqa_admin1985\n"
            "🚖 Taksi chaqirish: 'Taksi chaqirish' tugmasini bosing\n"
            "👥 Mijoz qidirish (haydovchilar uchun)\n"
            "🌐 Tilni o'zgartirish: 'Tilni o'zgartirish' tugmasi\n"
            "🔄 Rolni o'zgartirish: Admin bilan bog'laning\n\n"
            "Agar muammo bo'lsa: @ALoqa_admin1985"
        )
    else:
        help_text = (
            "🆘 Центр помощи\n\n"
            "📞 Поддержка: @ALoqa_admin1985\n"
            "🚖 Вызов такси: Нажмите 'Вызвать такси'\n"
            "👥 Поиск клиентов (для водителей)\n"
            "🌐 Смена языка: Кнопка 'Сменить язык'\n"
            "🔄 Смена роли: Свяжитесь с администратором\n\n"
            "Если есть проблемы: @ALoqa_admin1985"
        )
    
    await message.answer(help_text)

# Rolni o'zgartirish handler
@dp.message(F.text.in_(["🔄 Rolni o'zgartirish", "🔄 Сменить роль"]))
async def change_role_request(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id)
    
    if not user_data:
        await start_command(message)
        return
    
    language = user_data['language']
    current_role = user_data['role']
    
    if language == 'uz':
        text = (
            f"🔄 Rol o'zgartirish so'rovi\n\n"
            f"Joriy rol: {'Haydovchi' if current_role == 'driver' else 'Mijoz'}\n\n"
            f"Rolingizni o'zgartirish uchun admin @ALoqa_admin1985 ga murojaat qiling."
        )
    else:
        text = (
            f"🔄 Запрос на смену роли\n\n"
            f"Текущая роль: {'Водитель' if current_role == 'driver' else 'Клиент'}\n\n"
            f"Для смены роли обратитесь к администратору @ALoqa_admin1985."
        )
    
    await message.answer(text)
    
    # Adminga so'rov yuborish
    admin_text = (
        f"🔄 Rol o'zgartirish so'rovi:\n"
        f"👤 Foydalanuvchi: {user_data['first_name']}\n"
        f"📱 Username: @{user_data['username'] or 'Yoq'}\n"
        f"🆔 ID: {user_id}\n"
        f"🎯 Joriy rol: {'Haydovchi' if current_role == 'driver' else 'Mijoz'}\n"
        f"🌐 Til: {language}\n\n"
        f"Rolni o'zgartirish uchun quyidagi komandani yuboring:\n"
        f"/setrole_{user_id}_[yangi_rol]\n"
        f"Misol: /setrole_{user_id}_driver"
    )
    
    try:
        await bot.send_message(ADMIN_ID, admin_text)
    except Exception as e:
        logger.error(f"Adminga xabar yuborishda xatolik: {e}")

# Admin komandalari
@dp.message(Command("stats"))
async def admin_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Sizda admin huquqlari yo'q!")
        return
    
    total_users = len(users_db)
    drivers = len([u for u in users_db.values() if u.get('role') == 'driver'])
    customers = len([u for u in users_db.values() if u.get('role') == 'customer'])
    
    stats_text = (
        f"📊 Bot Statistikasi:\n\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"🚕 Haydovchilar: {drivers}\n"
        f"👤 Mijozlar: {customers}\n"
        f"📅 Hisobot vaqti: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await message.answer(stats_text)

# Admin rol o'zgartirish
@dp.message(F.text.startswith("/setrole_"))
async def admin_set_role(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Sizda admin huquqlari yo'q!")
        return
    
    try:
        parts = message.text.split('_')
        if len(parts) != 3:
            await message.answer("❌ Noto'g'ri format. Format: /setrole_USERID_ROLE")
            return
        
        target_user_id = int(parts[1])
        new_role = parts[2]  # 'driver' yoki 'customer'
        
        if target_user_id not in users_db:
            await message.answer("❌ Foydalanuvchi topilmadi!")
            return
        
        old_role = users_db[target_user_id].get('role')
        users_db[target_user_id]['role'] = new_role
        
        # Foydalanuvchiga xabar
        user_lang = users_db[target_user_id].get('language', 'uz')
        
        if user_lang == 'uz':
            user_text = f"✅ Sizning rolingiz {'Haydovchi' if new_role == 'driver' else 'Mijoz'} ga o'zgartirildi!"
        else:
            user_text = f"✅ Ваша роль изменена на {'Водитель' if new_role == 'driver' else 'Клиент'}!"
        
        try:
            await bot.send_message(target_user_id, user_text)
        except Exception as e:
            logger.error(f"Foydalanuvchiga xabar yuborishda xatolik: {e}")
        
        # Adminga tasdiq
        admin_text = (
            f"✅ Rol muvaffaqiyatli o'zgartirildi!\n"
            f"👤 Foydalanuvchi: {users_db[target_user_id]['first_name']}\n"
            f"🆔 ID: {target_user_id}\n"
            f"🔄 Eski rol: {'Haydovchi' if old_role == 'driver' else 'Mijoz'}\n"
            f"🆕 Yangi rol: {'Haydovchi' if new_role == 'driver' else 'Mijoz'}"
        )
        
        await message.answer(admin_text)
        
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")
        logger.error(f"Rol o'zgartirishda xatolik: {e}")

# Boshqa barcha xabarlar uchun
@dp.message()
async def handle_other_messages(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id)
    
    if not user_data:
        await start_command(message)
        return
    
    language = user_data['language']
    
    if language == 'uz':
        text = "❌ Noma'lum buyruq. Iltimos, menyudan foydalaning."
    else:
        text = "❌ Неизвестная команда. Пожалуйста, используйте меню."
    
    await message.answer(text)
    await show_main_menu(message, user_data)

# Asosiy funksiya
async def main():
    logger.info("🤖 Bot ishga tushdi...")
    logger.info(f"👮 Admin ID: {ADMIN_ID}")
    logger.info(f"📱 Admin username: {ADMIN_USERNAME}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())