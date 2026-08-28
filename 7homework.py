import asyncio
import os
import sqlite3
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
load_dotenv()
TOKEN=os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

DAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
]
def init_db():
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT,
            subject TEXT,
            time TEXT,
            room TEXT
        )
    """
    )
    conn.commit()
    conn.close()

class AddLesson(StatesGroup):
    day = State()
    subject = State()
    time = State()
    room = State()
def get_main_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Добавить занятие", callback_data="add")],
        [InlineKeyboardButton(text="Показать все", callback_data="show_all")],
        [InlineKeyboardButton(text="Выбрать день", callback_data="choose_day")],
        [InlineKeyboardButton(text="Удалить занятие", callback_data="delete")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_days_keyboard(prefix: str):
    buttons = []
    for day in DAYS:
        buttons.append(
            [InlineKeyboardButton(text=day, callback_data=f"{prefix}:{day}")]
        )
    buttons.append([InlineKeyboardButton(text="Назад", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот для хранения расписания. Выбери действие:",
        reply_markup=get_main_keyboard(),
    )
@dp.callback_query(F.data == "main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Выбери действие:", reply_markup=get_main_keyboard()
    )
    await callback.answer()
@dp.callback_query(F.data == "show_all")
async def show_all_lessons(callback: CallbackQuery):
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT day, subject, time, room 
        FROM lessons  
        ORDER BY id
        """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        text = "Расписание пусто."
    else:
        text = "Полное расписание:\n\n"
        for row in rows:
            text += f"📅 *{row[0]}*\n📖 {row[1]} | 🕒 {row[2]} | 🚪 каб. {row[3]}\n\n"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="main")]
        ]
    )
    await callback.message.edit_text(
        text, parse_mode="Markdown", reply_markup=kb
    )
    await callback.answer()

@dp.callback_query(F.data == "choose_day")
async def choose_day_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выбери день недели:", reply_markup=get_days_keyboard("view")
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("view:"))
async def show_day_lessons(callback: CallbackQuery):
    day = callback.data.split(":")[1]

    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    cursor.execute(
        """SELECT subject, time, room
        FROM lessons
        WHERE day = ?""",
        (day,)
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        text = f"На {day} занятий нет."
    else:
        text = f"Расписание на *{day}*:\n\n"
        for row in rows:
            text += f"📖 {row[0]} 🕒 {row[1]} 🚪 каб. {row[2]}\n"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="choose_day")]
        ]
    )
    await callback.message.edit_text(
        text, parse_mode="Markdown", reply_markup=kb
    )
    await callback.answer()
@dp.callback_query(F.data == "add")
async def add_lesson_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddLesson.day)
    await callback.message.edit_text(
        "Выбери день недели:",
        reply_markup=get_days_keyboard("add_day")
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("add_day:"), AddLesson.day)
async def add_lesson_day(callback: CallbackQuery, state: FSMContext):
    day = callback.data.split(":")[1]
    await state.update_data(day=day)
    await state.set_state(AddLesson.subject)
    await callback.message.edit_text(" Введи название предмета:")
    await callback.answer()


@dp.message(AddLesson.subject)
async def add_lesson_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(AddLesson.time)
    await message.answer(" Введи время:")
@dp.message(AddLesson.time)
async def add_lesson_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(AddLesson.room)
    await message.answer(" Введи кабинет:")

@dp.message(AddLesson.room)
async def add_lesson_room(message: Message, state: FSMContext):
    await state.update_data(room=message.text)
    data = await state.get_data()
    await state.clear()
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO lessons (day, subject, time, room) 
        VALUES (?, ?, ?, ?),
        (data["day"], data["subject"], data["time"], data["room"]),
    """)
    conn.commit()
    conn.close()

    await message.answer(
        f"✅ Занятие успешно добавлено!\n"
        f"📅 {data['day']} 📖 {data['subject']} 🕒 {data['time']} 🚪 каб. {data['room']}",
        reply_markup=get_main_keyboard(),
    )
@dp.callback_query(F.data == "delete")
async def delete_lesson_menu(callback: CallbackQuery):
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, day, subject, time 
        FROM lessons 
        ORDER BY id
        """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data="main")]
            ]
        )
        await callback.message.edit_text("Нечего удалять.", reply_markup=kb)
        await callback.answer()
        return

    buttons = []
    for row in rows:
       
        btn_text = f"❌ {row[1][:3]}. | {row[2][:10]} | {row[3]}"
        buttons.append(
            [InlineKeyboardButton(text=btn_text, callback_data=f"del:{row[0]}")]
        )

    buttons.append([InlineKeyboardButton(text="Назад", callback_data="main")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        "Выбери занятие для удаления:", reply_markup=kb
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("del:"))
async def delete_lesson_confirm(callback: CallbackQuery):
    lesson_id = int(callback.data.split(":")[1])

    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM lessons 
        WHERE id = ?,
        """)

    (lesson_id,)
    conn.commit()
    conn.close()

    await callback.answer("Занятие удалено!")
    await delete_lesson_menu(callback)


async def main():
    init_db() 
    await dp.start_polling(bot)  


if __name__ == "__main__":
    asyncio.run(main())
