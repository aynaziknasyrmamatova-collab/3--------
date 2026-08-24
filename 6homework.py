import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
TOKEN="8652006388:AAE-t1_TQI0GYJ-kaKSAYWbpGhKgo-S26Ko"
bot=Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)
dp=Dispatcher(
    storage=MemoryStorage()
)
conn=sqlite3.connect("tasks.db")
cur=conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL
)
""")
conn.commit()
class AddTask(StatesGroup):
    title=State()
    description=State()
class EditTask(StatesGroup):
    task_id=State()
    desciprion=State()
def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Добавить задачу",
                    callback_data="add_task"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Мои задачи",
                    callback_data="my_tasks"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Изменить задачу",
                    callback_data="edit_task"

                )
            ],
            [
                InlineKeyboardButton(
                    text="Удалить задачу",
                    callback_data="delete_task"
                )
            ]
        ]
    )
@dp.message(F.text=="/start")
async def start(message:Message):
    await message.answer(
        "<b>Мои задачи</b>\n\n"
        "Здесь вы можете создавать и хрнаить свои задачи",
        reply_markup=main_menu()

    )
@dp.callback_query(F.data=="add_task")
async def add(
    callback:CallbackQuery,
    state:FSMContext
):
    await callback.answer()
    await callback.message.answer(
        "Добавление новой задачи\n\n"
        "Введите название задачи:"
    )
    await state.set_state(AddTask.title)
@dp.message(AddTask.title)
async def get_title(
    message:Message,
    state:FSMContext
):
    await state.update_data(
        title=message.text
    )
    await message.answer(
        "Введите свои задачи:"
    )
    await state.set_state(AddTask.description)
@dp.message(AddTask.description)
async def get_text(
    message:Message,
    state:FSMContext
):
    data=await state.get_data()
    title=data["title"]
    description=message.text
    telegram_id=message.from_user.id
    cur.execute(
        """
        INSERT INTO tasks
        (telegram_id, title, description)
        VALUES (?,?,?)
        """,
        (
            telegram_id,
            title,
            description
        )
    )
    conn.commit()
    await state.clear()
    await message.answer(
        "Задача сохранена\n\n"
        f"<b>{title}</b>\n"
        f"{description}",
        reply_markup=main_menu()
    )
@dp.callback_query(F.data=="my_tasks")
async def my_tasks(callback:CallbackQuery):
    telegram_id=callback.from_user.id
    cur.execute(
        """
        SELECT id,title, description
        FROM tasks
        WHERE telegram_id=?
        """,
        (telegram_id,)
    )
    tasks=cur.fetchall()
    if not tasks:
        await callback.answer()
        await callback.message.answer(
            "У вас пока нет задач",
            reply_markup=main_menu()
        )
        return
    text="<b>Ваши задачи:</b>\n\n"
    for task in tasks:
        task_id, title, task_description=task
        text+=(
            f"ID: {task_id}\n"
            f"<b>{title}</b>\n"
            f"{task_description}\n"
        )
    await callback.answer()
    await callback.message.answer(
        text,
        reply_markup=main_menu()
    )
@dp.callback_query(F.data=="edit_task")
async def edit_task(
    callback:CallbackQuery,
    state:FSMContext
):
    telegram_id= callback.from_user.id
    cur.execute(
        """
        SELECT id, title
        FROM tasks
        WHERE telegram_id=?
        """,
        (telegram_id,)
    )
    tasks=cur.fetchall()
    if not tasks:
        await callback.answer(
            "У вас нет задач"
        )
        return
    buttons=[]
    for task_id, title in tasks:
        buttons.append([
            InlineKeyboardButton(
                text=title,
                callback_data=f"edit:{task_id}"
            )
        ])
    keyboard=InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
    await callback.answer()
    await callback.message.answer(
        "Выбери задачу, которую хотите извенить:",
        reply_markup=keyboard
    )
@dp.callback_query(F.data.startswith("edit"))
async def choose(
    callback:CallbackQuery,
    state:FSMContext
):
    task_id=int(
        callback.data.split(":")[1]
    )
    await state.update_data(
        task_id=task_id
    )
    await callback.answer()
    await callback.message.answer(
        "Введите новую задачу:"
    )
    await state.set_state(
        EditTask.desciprion
    )
@dp.message(EditTask.desciprion)
async def update_task(
    message:Message,
    state:FSMContext
):
    data=await state.get_data()
    task_id=data["task_id"]
    telegram_id=message.from_user.id
    new_description=message.text
    cur.execute(
        """
        UPDATE tasks
        SET description=?
        WHERE id=?
        AND telegram_id=?
        """,
        (
            new_description,
            task_id,
            telegram_id
        )
    )
    conn.commit()
    await state.clear()
    if cur.rowcount==0:
        await message.answer(
            "Задача не найдена"
        )
        return
    await message.answer(
        "Задача изменена:",
        reply_markup=main_menu()
    )
@dp.callback_query(F.data=="delete_task")
async def delete(
    callback:CallbackQuery
):
    telegram_id=callback.from_user.id
    cur.execute(
        """
        SELECT id, title
        FROM tasks
        WHERE telegram_id=?
        """,
        (telegram_id,)
    )
    tasks=cur.fetchall()
    if not tasks:
        await callback.answer(
            "У вас пока нет задач"
        )
        return

    buttons=[]
    for task_id, title in tasks:
        buttons.append([
            InlineKeyboardButton(
                text=title,
                callback_data=f"delete:{task_id}"
            )
        ])
    keyboard=InlineKeyboardMarkup(
        inline_keyboard=buttons
    )
    await callback.answer()
    await callback.message.answer(
        "Выберите задачу для удаления:",
        reply_markup=keyboard
    )
@dp.callback_query(F.data.startswith("delete:"))
async def delete_note(
    callback:CallbackQuery
):
    task_id=int(
        callback.data.split(":")[1]
    )
    telegram_id=callback.from_user.id
    cur.execute(
        """
        DELETE FROM tasks
        WHERE id=?
        AND telegram_id=?
        """,
        (
            task_id,
            telegram_id
        )
    )
    conn.commit()
    if cur.rowcount==0:
        await callback.answer(
            "Задача не найдена"
        )
        return
    await callback.answer()
    await callback.message.answer(
        "Заметка удалена",
        reply_markup=main_menu()
    )

async def main():
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())