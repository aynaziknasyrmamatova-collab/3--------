import asyncio
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

TOKEN = "8652006388:AAFeqcrQPs2GQ5sME_R3TcYf5c_LI8uATiA"

bot = Bot(token=TOKEN)
dp = Dispatcher()
conn = sqlite3.connect("users.db")
cur = conn.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        age INTEGER,
        city TEXT,
        street TEXT,
        phone INTEGER
    )
    """
)
conn.commit()


@dp.message(F.text == "/start")
async def start(message: Message):
    telegram_id = message.from_user.id
    name = message.from_user.first_name or "Пользователь"
    surname = message.from_user.last_name or "Пользователь"

    cur.execute(
        "SELECT * FROM users WHERE telegram_id=?",
        (telegram_id,),
    )
    person = cur.fetchone()
    if person:
        await message.answer(
            "Ты уже есть в базе данных\n"
            "Команды:\n"
            "/me - мой профиль\n"
            "/users - список пользователей"
        )
        return

    cur.execute(
        "INSERT INTO users (telegram_id, name, surname) VALUES (?,?,?)",
        (telegram_id, name, surname),
    )
    conn.commit()
    await message.answer(
        f"Привет, {name}!\n\n"
        "Ты зарегистрирован/а и сохранен/а в базу данных.\n\n"
        "Команды:\n"
        "/me - мой профиль\n"
        "/users - список пользователей"
    )


@dp.message(F.text == "/me")
async def profile(message: Message):
    telegram_id = message.from_user.id
    cur.execute(
        "SELECT id, name, surname, age, city, phone, street FROM users WHERE telegram_id=?",
        (telegram_id,),
    )
    user = cur.fetchone()
    if not user:
        await message.answer("Ты еще не зарегистрирован/а.\nНапиши /start")
        return

    user_id, name, surname, age, city, phone, street = user
    age = age if age is not None else "Не указан"
    city = city if city else "Не указан"
    phone = phone if phone is not None else "Не указан"
    street = street if street else "Не указана"

    await message.answer(
        f"Твой профиль\n\n"
        f"ID: {user_id}\n"
        f"Имя: {name}\n"
        f"Фамилия: {surname}\n"
        f"Возраст: {age}\n"
        f"Город: {city}\n"
        f"Номер телефона: {phone}\n"
        f"Улица: {street}"
    )


@dp.message(F.text == "/users")
async def users(message: Message):
    cur.execute("SELECT id, name, surname, age, city, phone, street FROM users")
    users_list = cur.fetchall()
    if not users_list:
        await message.answer("В базе пока нет пользователей")
        return

    text = "Пользователи:\n\n"
    for user_id, name, surname, age, city, phone, street in users_list:
        text += (
            f"ID: {user_id}\n"
            f"Имя: {name}\n"
            f"Фамилия: {surname}\n"
            f"Возраст: {age if age is not None else 'Не указан'}\n"
            f"Город: {city if city else 'Не указан'}\n"
            f"Номер телефона: {phone if phone is not None else 'Не указан'}\n"
            f"Улица: {street if street else 'Не указана'}\n\n"
        )
    await message.answer(text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

