import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = "7991412037:AAHaFKmWk1UzdHLBobw5DUYq94UJD0v4S5k"
ADMIN_ID = 907402803
MOVIE_FILE = "movies.json"
USER_FILE = "users.json"
CONFIG_FILE = "config.json"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

# Fayl o‘qish/yozish funksiyalari
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"channel_username": None}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=4)

def load_movies():
    try:
        with open(MOVIE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_movies():
    with open(MOVIE_FILE, "w", encoding="utf-8") as file:
        json.dump(movies, file, ensure_ascii=False, indent=4)

def load_users():
    try:
        with open(USER_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users():
    with open(USER_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

# Global o‘zgaruvchilar
config = load_config()
CHANNEL_USERNAME = config.get("channel_username")
adding_channel_id = {}
adding_movie_code = {}
sending_broadcast_message = {}
movies = load_movies()
users = load_users()

# Menular
main_menu = ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)

admin_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🔑 Admin Panel")],
    [KeyboardButton(text="📊 Foydalanuvchilar")],
    [KeyboardButton(text="⚙️ Kanal sozlash")],
    [KeyboardButton(text="📢 Xabar yuborish")]
], resize_keyboard=True)

admin_panel_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="➕ Yangi kino qo‘shish")],
    [KeyboardButton(text="📤 Video yuklash")],
    [KeyboardButton(text="📊 Foydalanuvchilar")],
    [KeyboardButton(text="⚙️ Kanal sozlash")],
    [KeyboardButton(text="📢 Xabar yuborish")],
    [KeyboardButton(text="⬅️ Asosiy menyu")]
], resize_keyboard=True)

# /start komandasi
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

# Admin panel
@dp.message(lambda m: m.text == "🔑 Admin Panel")
async def admin_panel(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🔑 Admin paneliga xush kelibsiz!", reply_markup=admin_panel_menu)
    else:
        await message.answer("❌ Siz admin emassiz!")

# Kino qo‘shish bosqichlari
@dp.message(lambda m: m.text == "➕ Yangi kino qo‘shish")
async def add_movie_step1(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("📌 Kino kodi kiriting:")
        adding_movie_code[message.from_user.id] = {"step": "waiting_for_code"}

@dp.message(lambda m: m.from_user.id in adding_movie_code and adding_movie_code[m.from_user.id]["step"] == "waiting_for_code")
async def add_movie_step2(message: Message):
    code = message.text
    if not code.strip():
        return await message.answer("⚠️ Kino kodi bo‘sh bo‘lishi mumkin emas!")
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

# Video yuklash bosqichlari
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

# Kino yuborish
@dp.message(lambda m: m.text in movies)
async def send_movie(message: Message):
    code = message.text
    user_id = message.from_user.id
    if user_id == ADMIN_ID or (CHANNEL_USERNAME and (await bot.get_chat_member(CHANNEL_USERNAME, user_id)).status in ["member", "administrator", "creator"]) or not CHANNEL_USERNAME:
        file_id = movies[code].get("file_id")
        if file_id:
            await bot.send_video(chat_id=message.chat.id, video=file_id, protect_content=True)
        else:
            await message.answer("⚠️ Kino hali yuklanmagan!")
    else:
        invite_link = await bot.export_chat_invite_link(chat_id=CHANNEL_USERNAME)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Kanalga qo‘shilish", url=invite_link)]])
        await message.answer("⚠️ Kanalga obuna bo‘ling!", reply_markup=keyboard)

# Menuga qaytish
@dp.message(lambda m: m.text == "⬅️ Asosiy menyu")
async def back_to_main(message: Message):
    await message.answer("🔙 Asosiy menyu", reply_markup=admin_menu if message.from_user.id == ADMIN_ID else main_menu)

# Foydalanuvchilar soni
@dp.message(lambda m: m.text == "📊 Foydalanuvchilar")
async def list_users(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(f"👥 Bot foydalanuvchilari soni: {len(users)}")

# Kanal sozlash
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

# Xabar yuborish
@dp.message(lambda m: m.text == "📢 Xabar yuborish")
async def broadcast_message_step1(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("✍️ Barcha foydalanuvchilarga yuboriladigan xabarni kiriting:")
        sending_broadcast_message[message.from_user.id] = {"step": "waiting_for_message"}

@dp.message(lambda m: m.from_user.id in sending_broadcast_message and sending_broadcast_message[m.from_user.id]["step"] == "waiting_for_message")
async def broadcast_message_step2(message: Message):
    admin_id = message.from_user.id
    broadcast_text = message.text
    sent_count = 0
    failed_count = 0

    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id, text=broadcast_text)
            sent_count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            failed_count += 1
            print(f"Xabar yuborishda xatolik (Foydalanuvchi ID: {user_id}): {e}")

    await message.answer(f"✅ Xabar {sent_count} ta foydalanuvchiga yuborildi.\n❌ {failed_count} ta foydalanuvchiga yuborilmadi.")
    del sending_broadcast_message[admin_id]

# Noto‘g‘ri kino kodi
@dp.message(lambda m: m.text and m.text not in movies and m.text not in [
    "🔑 Admin Panel", "📊 Foydalanuvchilar", "⚙️ Kanal sozlash", "⬅️ Asosiy menyu",
    "➕ Yangi kino qo‘shish", "📤 Video yuklash", "📢 Xabar yuborish"
] and not m.text.startswith("/"))
async def movie_not_found(message: Message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID or (CHANNEL_USERNAME and (await bot.get_chat_member(CHANNEL_USERNAME, user_id)).status in ["member", "administrator", "creator"]) or not CHANNEL_USERNAME:
        await message.answer("❌ Bunday kino mavjud emas!")
    else:
        invite_link = await bot.export_chat_invite_link(chat_id=CHANNEL_USERNAME)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Kanalga qo‘shilish", url=invite_link)]])
        await message.answer("⚠️ Kanalga obuna bo‘ling!", reply_markup=keyboard)

# Botni ishga tushirish
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
