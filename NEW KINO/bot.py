import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

TOKEN = "8072672790:AAH0vfEJMn34EBKWnsluaeKkmRSSiMx6h90"
ADMIN_ID = 907402803
MOVIE_FILE = "movies.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🎬 Fayldan kinolarni yuklash
def load_movies():
    try:
        with open(MOVIE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# 🎬 Kinolarni faylga yozish
def save_movies():
    with open(MOVIE_FILE, "w", encoding="utf-8") as file:
        json.dump(movies, file, ensure_ascii=False, indent=4)

movies = load_movies()  # Bot ishga tushganda yuklaymiz
adding_movie_code = {}

# 🎬 Asosiy menu
main_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🎥 Kinolar ro‘yxati")]],
    resize_keyboard=True
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎥 Kinolar ro‘yxati")],
        [KeyboardButton(text="🔑 Admin Panel")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🎬 Salom, admin!", reply_markup=admin_menu)
    else:
        await message.answer("🎬 Salom! Kino kodini kiriting", reply_markup=main_menu)

@dp.message(lambda message: message.text == "🎥 Kinolar ro‘yxati")
async def list_movies(message: Message):
    if not movies:
        return await message.answer("📭 Hozircha kinolar yo‘q.")

    buttons = [[KeyboardButton(text=code)] for code in movies.keys()]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("📽 Kino kodini tanlang:", reply_markup=keyboard)

@dp.message(lambda message: message.text == "🔑 Admin Panel")
async def admin_panel(message: Message):
    if message.from_user.id == ADMIN_ID:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="➕ Yangi kino qo‘shish")],
                [KeyboardButton(text="📤 Video yuklash")],
                [KeyboardButton(text="⬅️ Asosiy menyu")]
            ],
            resize_keyboard=True
        )
        await message.answer("🔑 Admin paneliga xush kelibsiz!", reply_markup=keyboard)
    else:
        await message.answer("❌ Siz admin emassiz!")

@dp.message(lambda message: message.text == "➕ Yangi kino qo‘shish")
async def add_movie_step1(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("📌 Kino kodi kiriting:")
        adding_movie_code[message.from_user.id] = {"step": "waiting_for_code"}
    else:
        await message.answer("❌ Siz admin emassiz!")

@dp.message(lambda message: message.from_user.id in adding_movie_code and adding_movie_code[message.from_user.id]["step"] == "waiting_for_code")
async def add_movie_step2(message: Message):
    code = message.text
    if code in movies:
        return await message.answer("⚠️ Bunday kod allaqachon bor!")

    adding_movie_code[message.from_user.id]["code"] = code
    adding_movie_code[message.from_user.id]["step"] = "waiting_for_name"
    await message.answer("📌 Kino nomini kiriting:")

@dp.message(lambda message: message.from_user.id in adding_movie_code and adding_movie_code[message.from_user.id]["step"] == "waiting_for_name")
async def add_movie_step3(message: Message):
    name = message.text
    code = adding_movie_code[message.from_user.id]["code"]

    movies[code] = {"name": name, "file_id": None}
    save_movies()  # Kino qo‘shilgandan keyin JSON faylga yozamiz

    del adding_movie_code[message.from_user.id]
    await message.answer(f"✅ Kino '{name}' kodi '{code}' bilan qo‘shildi!")

@dp.message(lambda message: message.text == "📤 Video yuklash")
async def upload_video_step1(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("📌 Qaysi kod uchun video yuklamoqchisiz?")
        adding_movie_code[message.from_user.id] = {"step": "waiting_for_video_code"}
    else:
        await message.answer("❌ Siz admin emassiz!")

@dp.message(lambda message: message.from_user.id in adding_movie_code and adding_movie_code[message.from_user.id]["step"] == "waiting_for_video_code")
async def upload_video_step2(message: Message):
    code = message.text
    if code not in movies:
        return await message.answer("❌ Bunday kodli kino mavjud emas!")

    adding_movie_code[message.from_user.id]["code"] = code
    adding_movie_code[message.from_user.id]["step"] = "waiting_for_video"
    await message.answer("📌 Endi ushbu kod uchun videoni jo‘nating:")

@dp.message(lambda message: message.from_user.id in adding_movie_code and adding_movie_code[message.from_user.id]["step"] == "waiting_for_video")
async def receive_video(message: Message):
    if not message.video:
        return await message.answer("❌ Iltimos, video yuboring!")

    code = adding_movie_code[message.from_user.id]["code"]
    movies[code]["file_id"] = message.video.file_id
    save_movies()  # Videoni JSON faylga yozamiz

    del adding_movie_code[message.from_user.id]
    await message.answer(f"✅ Kino '{movies[code]['name']}' yuklandi!")

@dp.message(lambda message: message.text in movies)
async def send_movie(message: Message):
    code = message.text
    if movies[code]["file_id"]:
        await message.answer_video(movies[code]["file_id"])
    else:
        await message.answer("⚠️ Kino hali yuklanmagan!")

@dp.message(lambda message: message.text == "⬅️ Asosiy menyu")
async def back_to_main(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🔙 Asosiy menyu", reply_markup=admin_menu)
    else:
        await message.answer("🔙 Asosiy menyu", reply_markup=main_menu)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
