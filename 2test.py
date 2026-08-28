import asyncio
import os
import sqlite3
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.client.default import DefaultBotProperties
load_dotenv()
TOKEN=os.getenv("BOT_TOKEN")
bot=Bot(
    token=TOKEN,
    default=DefaultBotProperties
)


dp=Dispatcher()
conn=sqlite3.connect("students.db")
cur=conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        name TEXT NOT NULL,
        age INTEGER
    )
    """)
conn.commit()
@dp.message("/start")
async def start(message:Message):
    telegram_id=message.from_user.id
    name=message.from_user.id or "Пользователь"
    cur.execute(
        """
        SELECT * FROM students,
        WHERE telegram_id=?,
        (telegram_id,)
"""
    )
    student=cur.fetchone()
    if student:
        await message.answer(
            "Ты уже есть в базе данных\n\n"
            "Команды:\n"
            "/me-мой профиль\n"
            "/students- список студентов"
        )
        return
    cur.execute("""
        INSERT INTO students(telegram_id,name) 
        VALUES(?,?),
        (telegram_id,)
    """)
    student=cur.fetchone()
    if not student:
        await message.answer("Тыы еще не арегистрирован")
        return
    student_id, name,age=student
    age=age if age is not None else "Не указан"
    city=city if city else "Не указан"
    await message.answer(
        f"Твой профиль\n\n"
        f"ID: {student_id}\n"
        f"Имя: {name}\n"
        f"Возраст: {age}"
    )
@dp.message(F.text=="/students")
async def students(message:Message):
    cur.execute("""
    SELECT id, name, age
    FROM students
""")
    students_list=cur.fetchall()
    if not students_list:
        await message.answer("В базе пока нет студентов")
        return
    text="Студенты:\n\n"
    for student_id, name,age in students_list:
        text+=(
            f"ID: {student_id}\n"
            f"Имя: {name}\n"
            f"Возраст: {age if age is not None else "Не указан"}"
        )
    await message.answer(text)
@dp.message(F.text == "Удалить студента")
async def delete_student(message: Message):
    telegram_id = message.from_user.id
    cur.execute(
        "SELECT id, name, age FROM students WHERE telegram_id = ?",
        (telegram_id,),
    )
    rows = cur.fetchall()
    if not rows:
        await message.answer("Список студентов пуст.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{name}",
                callback_data=f"del_{student_id}",
            )]
            for student_id, name in rows
        ]
    )
    await message.answer("Выберите студента, который хотите удалить:", reply_markup=keyboard)
async def main():
    await dp.start_polling(bot)
if __name__ =="__main__":
    asyncio.run(main())
#linux- это операционная система для компьютера 
#2. библиотка айограм нужна для быстрого и удобного создания телеграм бота
#3. callback это сообщение которое потом придет пользователю
#4. фсм это конечный автомат бота , который помогает понять на каком шаге находится пользователь
#5. база данных это место где можно хранить чьи-ьо данные
#6. sqlite это легкая беза данных которая позваоляет зранить в себе информацию
#7. insert- , select- выбрать , update- обновить , delete- удалить
#8. join помогает приявызывать вместе несколько таблиц
#9. inline кнопки помогают пользователю ориентироваться и давать команды боту
#10. они связаны тем что все необходимы для телеграм бота
