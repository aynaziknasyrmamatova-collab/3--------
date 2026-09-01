#список фильмов
#пользователь вводит название просмотренных фильмов, автора или режиссера и год выпуска
#бот затем это все сохраняет



import asyncio
import sqlite3
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
load_dotenv()


TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    year INTEGER
)
""")

conn.commit()

user_step = {}
user_movie = {}
def main_menu():

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Добавить фильм",
                    callback_data="add"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Мои фильмы",
                    callback_data="movies"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Изменить фильм",
                    callback_data="edit"
                ),
                InlineKeyboardButton(
                    text="🗑️ Удалить фильм",
                    callback_data="delete"
                )
            ]
        ]
    )

    return keyboard


@dp.message()
async def start(message: Message):

    if message.text == "/start":

        await message.answer(
            "🎬 Добро пожаловать в Movie List Bot!\n\n"
            "Здесь ты можешь хранить список просмотренных фильмов.",
            reply_markup=main_menu()
        )


@dp.callback_query(F.data == "add")
async def add_movie(callback: CallbackQuery):

    user_id = callback.from_user.id

    user_step[user_id] = "title"
    user_movie[user_id] = {}

    await callback.message.answer(
        "🎬 Введи название фильма:"
    )

    await callback.answer()


@dp.callback_query(F.data == "movies")
async def show_movies(callback: CallbackQuery):

    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()

    if len(movies) == 0:

        await callback.message.answer(
            "📋 Список фильмов пуст."
        )

    else:

        text = "🎬 Твои фильмы:\n\n"

        for movie in movies:

            text += (
                f"ID: {movie[0]}\n"
                f"🎬 {movie[1]}\n"
                f"✍️ {movie[2]}\n"
                f"📅 {movie[3]}\n\n"
            )

        await callback.message.answer(text)

    await callback.answer()
@dp.message()
async def add_information(message: Message):

    user_id = message.from_user.id

    if user_step.get(user_id) == "title":

        user_movie[user_id]["title"] = message.text
        user_step[user_id] = "author"

        await message.answer(
            "✍️ Введи автора или режиссёра:"
        )

    elif user_step.get(user_id) == "author":

        user_movie[user_id]["author"] = message.text
        user_step[user_id] = "year"

        await message.answer(
            "📅 Введи год выпуска:"
        )

    elif user_step.get(user_id) == "year":

        user_movie[user_id]["year"] = message.text

        cursor.execute(
            """
            INSERT INTO movies (title, author, year)
            VALUES (?, ?, ?)
            """,
            (
                user_movie[user_id]["title"],
                user_movie[user_id]["author"],
                user_movie[user_id]["year"]
            )
        )

        conn.commit()

        await message.answer(
            "✅ Фильм успешно добавлен!",
            reply_markup=main_menu()
        )

        user_step[user_id] = None
        user_movie[user_id] = None
@dp.callback_query(F.data == "delete")
async def delete_movie(callback: CallbackQuery):

    await callback.message.answer(
        "🗑️ Введи ID фильма, который хочешь удалить.\n\n"
        "Посмотреть ID можно через кнопку «📋 Мои фильмы»."
    )

    user_step[callback.from_user.id] = "delete"

    await callback.answer()
@dp.message()
async def delete_process(message: Message):

    user_id = message.from_user.id

    if user_step.get(user_id) == "delete":

        cursor.execute(
            "DELETE FROM movies WHERE id = ?",
            (message.text,)
        )

        conn.commit()

        await message.answer(
            "✅ Фильм удалён!",
            reply_markup=main_menu()
        )

        user_step[user_id] = None
@dp.callback_query(F.data == "edit")
async def edit_movie(callback: CallbackQuery):

    await callback.message.answer(
        "✏️ Введи ID фильма, который хочешь изменить.\n\n"
        "Посмотреть ID можно через кнопку «📋 Мои фильмы»."
    )

    user_step[callback.from_user.id] = "edit_id"

    await callback.answer()
@dp.message()
async def edit_process(message: Message):

    user_id = message.from_user.id

    if user_step.get(user_id) == "edit_id":

        user_movie[user_id] = {
            "id": message.text
        }

        user_step[user_id] = "edit_title"

        await message.answer(
            "🎬 Введи новое название фильма:"
        )

    elif user_step.get(user_id) == "edit_title":

        user_movie[user_id]["title"] = message.text

        user_step[user_id] = "edit_author"

        await message.answer(
            "✍️ Введи нового автора или режиссёра:"
        )

    elif user_step.get(user_id) == "edit_author":

        user_movie[user_id]["author"] = message.text

        user_step[user_id] = "edit_year"

        await message.answer(
            "📅 Введи новый год:"
        )

    elif user_step.get(user_id) == "edit_year":

        user_movie[user_id]["year"] = message.text

        cursor.execute(
            """
            UPDATE movies
            SET title = ?, author = ?, year = ?
            WHERE id = ?
            """,
            (
                user_movie[user_id]["title"],
                user_movie[user_id]["author"],
                user_movie[user_id]["year"],
                user_movie[user_id]["id"]
            )
        )

        conn.commit()

        await message.answer(
            "✅ Фильм успешно изменён!",
            reply_markup=main_menu()
        )

        user_step[user_id] = None
        user_movie[user_id] = None
async def main():

    print("Бот запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())