
import asyncio
import os
import sqlite3

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

conn = sqlite3.connect("courses.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS student_course (
    student_id INTEGER,
    course_id INTEGER,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
)
""")

conn.commit()


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Список курсов",
                    callback_data="courses"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Студенты курса",
                    callback_data="course_students"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Популярные курсы",
                    callback_data="popular"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Все студенты",
                    callback_data="students"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Управление",
                    callback_data="manage"
                )
            ]
        ]
    )
def manage_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Добавить курс",
                    callback_data="add_course"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Добавить студента",
                    callback_data="add_student"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Записаться на курс",
                    callback_data="enroll_help"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Удалить курс",
                    callback_data="delete_course"

                )
            ],
            [
                InlineKeyboardButton(
                    text="Удалить студента",
                    callback_data="delete_student"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Убрать с курса",
                    callback_data="unenroll"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Главное меню",
                    callback_data="main_menu"
                )
            ]
        ]
    )

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "<b>Курсы</b>\n\n"
        "Выберите нужный раздел:",
        reply_markup=main_menu()
    )
@dp.message(F.text=="/help")
async def help(message:Message):
    await message.answer(
        "<b>Курсы - помощь<b>\n\n"
        "<b>Добавление:<b>\n"
        "/add_course Geeks\n"
        "/add_student Ella\n"
        "/enroll 1 2 \n\n"
        "<b>Удаление:<b>\n"
        "/delete_course 1\n"
        "/delete_student 1\n"
        "/unenroll 1 2\n"
        "Где первое число - Id студента"
        "Второе - id курса"
    )
@dp.message(f.text.startswith)
@dp.callback_query(F.data == "courses")
async def show_courses(callback: CallbackQuery):
    cursor.execute("""
        SELECT id, title
        FROM courses
        ORDER BY title
    """)

    courses = cursor.fetchall()

    await callback.answer()

    if not courses:
        await callback.message.answer(
            "Курсов пока нет.",
            reply_markup=main_menu()
        )
        return

    text = "<b>Список курсов</b>\n\n"

    for course_id, title in courses:
        text += f"ID: {course_id}\n"
        text += f"Название: {title}\n"
        text += "--------------------\n"

    await callback.message.answer(
        text,
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "course_students")
async def choose_course(callback: CallbackQuery):
    cursor.execute("""
        SELECT id, title
        FROM courses
        ORDER BY title
    """)

    courses = cursor.fetchall()

    if not courses:
        await callback.answer("Курсов пока нет.")
        return

    buttons = []

    for course_id, title in courses:
        buttons.append([
            InlineKeyboardButton(
                text=title,
                callback_data=f"course:{course_id}"
            )
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.answer()

    await callback.message.answer(
        "Выберите курс:",
        reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("course:"))
async def show_course_students(callback: CallbackQuery):
    course_id = int(callback.data.split(":")[1])

    cursor.execute("""
        SELECT students.name, courses.title
        FROM student_course
        JOIN students
            ON students.id = student_course.student_id
        JOIN courses
            ON courses.id = student_course.course_id
        WHERE courses.id = ?
    """, (course_id,))

    students = cursor.fetchall()

    await callback.answer()

    if not students:
        await callback.message.answer(
            "На этот курс пока никто не записан.",
            reply_markup=main_menu()
        )
        return

    course_name = students[0][1]

    text = f"<b>Курс: {course_name}</b>\n\n"

    for index, (name, _) in enumerate(students, start=1):
        text += f"{index}. {name}\n"

    await callback.message.answer(
        text,
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "students")
async def show_students(callback: CallbackQuery):
    cursor.execute("""
        SELECT students.name, courses.title
        FROM student_course
        JOIN students
            ON students.id = student_course.student_id
        JOIN courses
            ON courses.id = student_course.course_id
        ORDER BY students.name
    """)

    rows = cursor.fetchall()

    await callback.answer()

    if not rows:
        await callback.message.answer(
            "Данных пока нет.",
            reply_markup=main_menu()
        )
        return

    text = "<b>Студенты и их курсы</b>\n\n"

    for name, course in rows:
        text += f"{name} — {course}\n"

    await callback.message.answer(
        text,
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "popular")
async def popular_courses(callback: CallbackQuery):
    cursor.execute("""
        SELECT courses.title,
               COUNT(student_course.student_id)
        FROM student_course
        JOIN courses
            ON courses.id = student_course.course_id
        GROUP BY courses.id
        HAVING COUNT(student_course.student_id) >= 2
        ORDER BY COUNT(student_course.student_id) DESC
    """)

    courses = cursor.fetchall()

    await callback.answer()

    if not courses:
        await callback.message.answer(
            "Пока нет курсов с двумя и более студентами.",
            reply_markup=main_menu()
        )
        return

    text = "<b>Популярные курсы</b>\n\n"

    for title, count in courses:
        text += f"{title} — {count} студентов\n"

    await callback.message.answer(
        text,
        reply_markup=main_menu()
    )


@dp.message(F.text == "/help")
async def help_command(message: Message):
    await message.answer(
        "<b>Курсы</b>\n\n"
        "/start — открыть меню\n"
        "/help — помощь"
    )


async def main():
    print("Бот Курсов запущен.")
    await dp.start_polling(bot)

async def main():
    print("Бот курсов запущен")
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
