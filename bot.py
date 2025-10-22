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
WEBAPP_URL = "https://rasulovmuhiddin4-bit.github.io/luxspeed-bot/webapp/"

# Bot va Dispatcher yaratish
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Ma'lumotlar bazasi
users_db = {}
orders_db = {}

# Til tanlash keyboard
def get_language_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Tilni tanlang..."
    )
    return keyboard

# Rol tanlash keyboard
def get_role_keyboard(language: str = 'uz'):
    if language == 'uz':
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🚕 Haydovchi"), KeyboardButton(text="👤 Mijoz")]
            ],
            resize_keyboard=True,
            input_field_placeholder="Rolni tanlang..."
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🚕 Водитель"), KeyboardButton(text="👤 Клиент")]
            ],
            resize_keyboard=True,
            input_field_placeholder="Выберите роль..."
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
            'language': None,
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
    
    # Agar hammasi tanlangan bo'lsa, WebApp ga yo'naltiramiz
    await redirect_to_webapp(message, user_data)

# WebApp ga yo'naltirish
async def redirect_to_webapp(message: Message, user_data: dict):
    user_id = message.from_user.id
    language = user_data['language']
    role = user_data['role']
    
    # WebApp URL
    web_app_url = f"{WEBAPP_URL}?user_id={user_id}&role={role}&lang={language}"
    
    if language == 'uz':
        if role == 'driver':
            text = "🚕 Haydovchi interfeysiga yo'naltirilmoqdasiz..."
            btn_text = "🚖 Haydovchi Interfeysi"
        else:
            text = "👤 Mijoz interfeysiga yo'naltirilmoqdasiz..."
            btn_text = "📱 Taksi Chaqirish"
    else:
        if role == 'driver':
            text = "🚕 Перенаправление в интерфейс водителя..."
            btn_text = "🚖 Интерфейс Водителя"
        else:
            text = "👤 Перенаправление в интерфейс клиента..."
            btn_text = "📱 Вызвать Такси"
    
    # Inline keyboard WebApp uchun
    webapp_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=btn_text, web_app=WebAppInfo(url=web_app_url))]]
    )
    
    await message.answer(text, reply_markup=webapp_keyboard)
    
    # Keyboard ni olib tashlaymiz
    await message.answer("⏳", reply_markup=ReplyKeyboardRemove())

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
    user_data = users_db.get(user_id)
    
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
    
    # WebApp ga yo'naltiramiz
    await redirect_to_webapp(message, user_data)
    
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

# Admin bilan aloqa
@dp.message(Command("admin"))
async def admin_contact(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id)
    
    if not user_data:
        await start_command(message)
        return
    
    language = user_data.get('language', 'uz')
    
    if language == 'uz':
        text = (
            f"👨‍💻 Admin bilan aloqa:\n\n"
            f"📞 Telegram: {ADMIN_USERNAME}\n"
            f"🌐 GitHub: https://github.com/rasulovmuhiddin4-bit/luxspeed-bot\n\n"
            f"🆘 Yordam kerak bo'lsa, admin bilan bog'laning."
        )
    else:
        text = (
            f"👨‍💻 Связь с администратором:\n\n"
            f"📞 Telegram: {ADMIN_USERNAME}\n"
            f"🌐 GitHub: https://github.com/rasulovmuhiddin4-bit/luxspeed-bot\n\n"
            f"🆘 Если нужна помощь, свяжитесь с администратором."
        )
    
    await message.answer(text)
    
# ... (oldingi kodlar o'zgarmaydi)

# Admin bilan aloqa handler
@dp.message(F.text.in_(["👨‍💻 Admin bilan aloqa", "👨‍💻 Связь с администратором"]))
async def admin_contact_button(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id)
    
    if not user_data:
        await start_command(message)
        return
    
    language = user_data.get('language', 'uz')
    
    if language == 'uz':
        text = (
            f"👨‍💻 Admin bilan aloqa:\n\n"
            f"📞 Telegram: {ADMIN_USERNAME}\n"
            f"🆔 Admin ID: {ADMIN_ID}\n\n"
            f"🆘 Yordam kerak bo'lsa, admin bilan bog'laning.\n"
            f"📝 Savol, taklif yoki shikoyatlaringiz bo'lsa yozib qoldiring."
        )
    else:
        text = (
            f"👨‍💻 Связь с администратором:\n\n"
            f"📞 Telegram: {ADMIN_USERNAME}\n"
            f"🆔 Admin ID: {ADMIN_ID}\n\n"
            f"🆘 Если нужна помощь, свяжитесь с администратором.\n"
            f"📝 Если у вас есть вопросы, предложения или жалобы, напишите."
        )
    
    # Keyboard qaytarish
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Asosiy menyu" if language == 'uz' else "🏠 Главное меню")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(text, reply_markup=keyboard)

# Asosiy menyuga qaytish
@dp.message(F.text.in_(["🏠 Asosiy menyu", "🏠 Главное меню"]))
async def back_to_main_menu(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id)
    
    if not user_data:
        await start_command(message)
        return
    
    await redirect_to_webapp(message, user_data)

# ... (qolgan kodlar o'zgarmaydi)    

# WebApp dan kelgan ma'lumotlarni qayta ishlash
@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    user_id = message.from_user.id
    
    try:
        web_app_data = json.loads(message.web_app_data.data)
        action = web_app_data.get('action')
        
        logger.info(f"WebApp ma'lumoti: {web_app_data}")
        
        if action == 'create_order':
            await handle_new_order(user_id, web_app_data)
        elif action == 'find_customer':
            await handle_find_customer(user_id, web_app_data)
        elif action == 'contact_admin':
            await admin_contact(message)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode xatosi: {e}")
    except Exception as e:
        logger.error(f"WebApp ma'lumotlarini qayta ishlashda xatolik: {e}")

# Yangi buyurtma yaratish
async def handle_new_order(user_id: int, data: dict):
    try:
        order_id = f"order_{user_id}_{int(datetime.now().timestamp())}"
        
        orders_db[order_id] = {
            'user_id': user_id,
            'customer_name': data.get('name'),
            'customer_phone': data.get('phone'),
            'from_location': data.get('from'),
            'to_location': data.get('to'),
            'payment_method': data.get('payment_method'),
            'language': data.get('language', 'uz'),
            'status': 'searching',
            'created_at': datetime.now().isoformat(),
            'price': data.get('price', '0')
        }
        
        # Foydalanuvchiga tasdiq
        user_lang = data.get('language', 'uz')
        if user_lang == 'uz':
            user_text = (
                f"✅ Buyurtma qabul qilindi!\n\n"
                f"🆔 Buyurtma raqami: {order_id}\n"
                f"👤 Ism: {data.get('name')}\n"
                f"📞 Telefon: {data.get('phone')}\n"
                f"📍 Manzil: {data.get('from')}\n"
                f"🎯 Yo'nalish: {data.get('to')}\n"
                f"💳 To'lov: {data.get('payment_method')}\n\n"
                f"🚕 Haydovchi qidirilmoqda..."
            )
        else:
            user_text = (
                f"✅ Заказ принят!\n\n"
                f"🆔 Номер заказа: {order_id}\n"
                f"👤 Имя: {data.get('name')}\n"
                f"📞 Телефон: {data.get('phone')}\n"
                f"📍 Адрес: {data.get('from')}\n"
                f"🎯 Направление: {data.get('to')}\n"
                f"💳 Оплата: {data.get('payment_method')}\n\n"
                f"🚕 Ищем водителя..."
            )
        
        await bot.send_message(user_id, user_text)
        
        # Adminga xabar
        admin_text = (
            f"🆕 Yangi buyurtma:\n\n"
            f"🆔 Buyurtma: {order_id}\n"
            f"👤 Mijoz: {data.get('name')}\n"
            f"📞 Telefon: {data.get('phone')}\n"
            f"📍 Manzil: {data.get('from')}\n"
            f"🎯 Yo'nalish: {data.get('to')}\n"
            f"💳 To'lov: {data.get('payment_method')}\n"
            f"🌐 Til: {data.get('language', 'uz')}\n"
            f"⏰ Vaqt: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        await bot.send_message(ADMIN_ID, admin_text)
        
    except Exception as e:
        logger.error(f"Buyurtma yaratishda xatolik: {e}")

# Mijoz qidirish
async def handle_find_customer(user_id: int, data: dict):
    try:
        user_data = users_db.get(user_id)
        if not user_data:
            return
        
        user_lang = user_data.get('language', 'uz')
        
        if user_lang == 'uz':
            text = "🔍 Mijozlar qidirilmoqda..."
        else:
            text = "🔍 Ищем клиентов..."
        
        await bot.send_message(user_id, text)
        
    except Exception as e:
        logger.error(f"Mijoz qidirishda xatolik: {e}")

# Boshqa barcha xabarlar uchun
@dp.message()
async def handle_other_messages(message: Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id)
    
    if not user_data:
        await start_command(message)
        return
    
    # Agar foydalanuvchi allaqachon rolni tanlagan bo'lsa, WebApp ga yo'naltiramiz
    if user_data.get('role'):
        await redirect_to_webapp(message, user_data)
    else:
        # Agar roli tanlanmagan bo'lsa, start boshlaymiz
        await start_command(message)

# Asosiy funksiya
async def main():
    logger.info("🤖 Bot ishga tushdi...")
    logger.info(f"👮 Admin ID: {ADMIN_ID}")
    logger.info(f"📱 Admin username: {ADMIN_USERNAME}")
    logger.info(f"🌐 WebApp URL: {WEBAPP_URL}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())