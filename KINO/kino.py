import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import F

TOKEN = "7991412037:AAE3lXzplwNiGoIjnPXyeop3LUoQWCyVBuk"
ADMIN_ID = 907402803  # ADMIN ID
MOVIE_FILE = "movies.json"
USER_FILE = "users.json"
CONFIG_FILE = "config.json"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

# ⚙️ Konfiguratsiya
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"channel_username": None}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=4)

config = load_config()
CHANNEL_USERNAME = config.get("channel_username")
adding_channel_id = {}

# 🎬 Kino va foydalanuvchilar
def load_movies():
    try:
        with open(MOVIE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return {}

def save_movies():
    with open(MOVIE_FILE, "w", encoding="utf-8") as file:
        json.dump(movies, file, ensure_ascii=False, indent=4)

def load_users():
    try:
        with open(USER_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return {}

def save_users():
    with open(USER_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

movies = load_movies()
users = load_users()
adding_movie_code = {}

main_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🎥 Kinolar ro‘yxati")]], resize_keyboard=True)
admin_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🎥 Kinolar ro‘yxati")],
    [KeyboardButton(text="🔑 Admin Panel")],
    [KeyboardButton(text="📊 Foydalanuvchilar")],
    [KeyboardButton(text="⚙️ Kanal sozlash")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "joined_at": message.date.isoformat()
        }
        save_users()

    if user_id == ADMIN_ID:
        await message.answer("🎬 Salom, admin!", reply_markup=admin_menu)
    else:
        if CHANNEL_USERNAME:
            chat_member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            if chat_member.status in ["member", "administrator", "creator"]:
                await message.answer("🎬 Salom! Kino kodini kiriting", reply_markup=main_menu)
            else:
                invite_link = await bot.export_chat_invite_link(chat_id=CHANNEL_USERNAME)
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Kanalga qo‘shilish", url=invite_link)]])
                await message.answer("⚠️ Botdan foydalanish uchun kanalga qo‘shiling:", reply_markup=keyboard)
        else:
            await message.answer("🎬 Salom! Kino kodini kiriting", reply_markup=main_menu)

@dp.message(lambda m: m.text == "🎥 Kinolar ro‘yxati")
async def list_movies(message: Message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID or (CHANNEL_USERNAME and (await bot.get_chat_member(CHANNEL_USERNAME, user_id)).status in ["member", "administrator", "creator"]) or not CHANNEL_USERNAME:
        if not movies:
            return await message.answer("📭 Hozircha kinolar yo‘q.")
        keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=code)] for code in movies], resize_keyboard=True)
        await message.answer("📽 Kino kodini tanlang:", reply_markup=keyboard)
    else:
        invite_link = await bot.export_chat_invite_link(chat_id=CHANNEL_USERNAME)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Kanalga qo‘shilish", url=invite_link)]])
        await message.answer("⚠️ Botdan foydalanish uchun kanalga qo‘shiling:", reply_markup=keyboard)

@dp.message(lambda m: m.text == "🔑 Admin Panel")
async def admin_panel(message: Message):
    if message.from_user.id == ADMIN_ID:
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="➕ Yangi kino qo‘shish")],
            [KeyboardButton(text="📤 Video yuklash")],
            [KeyboardButton(text="📊 Foydalanuvchilar")],
            [KeyboardButton(text="⚙️ Kanal sozlash")],
            [KeyboardButton(text="⬅️ Asosiy menyu")]
        ], resize_keyboard=True)
        await message.answer("🔑 Admin paneliga xush kelibsiz!", reply_markup=keyboard)
    else:
        await message.answer("❌ Siz admin emassiz!")

@dp.message(lambda m: m.text == "➕ Yangi kino qo‘shish")
async def add_movie_step1(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("📌 Kino kodi kiriting:")
        adding_movie_code[message.from_user.id] = {"step": "waiting_for_code"}

@dp.message(lambda m: m.from_user.id in adding_movie_code and adding_movie_code[m.from_user.id]["step"] == "waiting_for_code")
async def add_movie_step2(message: Message):
    code = message.text
    if code in movies:
        return await message.answer("⚠️ Bunday kod allaqachon bor!")
    adding_movie_code[message.from_user.id] = {"step": "waiting_for_name", "code": code}
    await message.answer("📌 Kino nomini kiriting:")

@dp.message(lambda m: m.from_user.id in adding_movie_code and adding_movie_code[m.from_user.id]["step"] == "waiting_for_name")
async def add_movie_step3(message: Message):
    data = adding_movie_code.pop(message.from_user.id)
    movies[data["code"]] = {"name": message.text, "file_id": None}
    save_movies()
    await message.answer(f"✅ Kino '{message.text}' kodi '{data['code']}' bilan qo‘shildi!")

@dp.message(lambda m: m.text == "📤 Video yuklash")
async def upload_video_step1(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("📌 Kodni kiriting:")
        adding_movie_code[message.from_user.id] = {"step": "waiting_for_video_code"}

@dp.message(lambda m: m.from_user.id in adding_movie_code and adding_movie_code[m.from_user.id]["step"] == "waiting_for_video_code")
async def upload_video_step2(message: Message):
    code = message.text
    if code not in movies:
        return await message.answer("❌ Bunday kod mavjud emas!")
    adding_movie_code[message.from_user.id] = {"step": "waiting_for_video", "code": code}
    await message.answer("📌 Endi video yuboring:")

@dp.message(lambda m: m.from_user.id in adding_movie_code and adding_movie_code[m.from_user.id]["step"] == "waiting_for_video")
async def receive_video(message: Message):
    if not message.video:
        return await message.answer("❌ Faqat video yuboring!")
    data = adding_movie_code.pop(message.from_user.id)
    movies[data["code"]]["file_id"] = message.video.file_id
    save_movies()
    await message.answer("✅ Video saqlandi!")

@dp.message(lambda m: m.text in movies)
async def send_movie(message: Message):
    code = message.text
    user_id = message.from_user.id
    if user_id == ADMIN_ID or (CHANNEL_USERNAME and (await bot.get_chat_member(CHANNEL_USERNAME, user_id)).status in ["member", "administrator", "creator"]) or not CHANNEL_USERNAME:
        file_id = movies[code].get("file_id")
        if file_id:
            await message.answer_video(file_id)
        else:
            await message.answer("⚠️ Kino hali yuklanmagan!")
    else:
        invite_link = await bot.export_chat_invite_link(chat_id=CHANNEL_USERNAME)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Kanalga qo‘shilish", url=invite_link)]])
        await message.answer("⚠️ Kanalga obuna bo‘ling!", reply_markup=keyboard)

@dp.message(lambda m: m.text == "⬅️ Asosiy menyu")
async def back_to_main(message: Message):
    await message.answer("🔙 Asosiy menyu", reply_markup=admin_menu if message.from_user.id == ADMIN_ID else main_menu)

@dp.message(lambda m: m.text == "📊 Foydalanuvchilar")
async def list_users(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(f"👥 Bot foydalanuvchilari soni: {len(users)}")

@dp.message(lambda m: m.text == "⚙️ Kanal sozlash")
async def set_channel_step1(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("📌 Kanal username’ni kiriting (masalan, `@kanalim`):")
        adding_channel_id[message.from_user.id] = {"step": "waiting_for_channel_id"}

@dp.message(lambda m: m.from_user.id in adding_channel_id and adding_channel_id[m.from_user.id]["step"] == "waiting_for_channel_id")
async def set_channel_step2(message: Message):
    username = message.text.strip()
    if not username.startswith("@"):
        return await message.answer("❌ '@' bilan boshlanadigan kanal username kiriting.")
    config["channel_username"] = username
    global CHANNEL_USERNAME
    CHANNEL_USERNAME = username
    save_config(config)
    await message.answer(f"✅ Kanal saqlandi: {username}")
    del adding_channel_id[message.from_user.id]

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
