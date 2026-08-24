import asyncio

import sqlite3
from html import escape


from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
TOKEN="8652006388:AAFj2ygPuIFZhK7W46xQOE7Sb9JThvr4Dw0"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
conn = sqlite3.connect("notes.db")
cur = conn.cursor()
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        text TEXT NOT NULL
    )
    """
)
conn.commit()


class AddNote(StatesGroup):
    title = State()
    text = State()


class EditNote(StatesGroup):
    note_id = State()
    text = State()


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить заметку", callback_data="add_note")],
            [InlineKeyboardButton(text="Мои заметки", callback_data="my_notes")],
            [InlineKeyboardButton(text="Изменить заметку", callback_data="edit_note")],
            [InlineKeyboardButton(text="Удалить заметку", callback_data="delete_note")],
        ]
    )


@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "МОИ ЗАМЕТКИ\n\n"
        "Здесь ты можешь создавать и хранить свои заметки.",
        reply_markup=main_menu(),
    )


@dp.callback_query(F.data == "add_note")
async def add(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Добавляем новую заметку\n\n""Напишите название заметки")
    await state.set_state(AddNote.title)


@dp.message(AddNote.title)
async def get_note(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Теперь напишите текст заметки:")
    await state.set_state(AddNote.text)


@dp.message(AddNote.text)
async def get_note_text(message: Message, state: FSMContext):
    data = await state.get_data()
    title = data["title"]
    note_text = message.text
    telegram_id = message.from_user.id
    cur.execute(
        "INSERT INTO notes (telegram_id, title, text) VALUES (?, ?, ?)",
        (telegram_id, title, note_text),
    )
    conn.commit()
    await state.clear()
    await message.answer(
        f"Заметка сохранена!\n\n{escape(title)}\n{escape(note_text)}",
        reply_markup=main_menu(),
    )


@dp.callback_query(F.data == "my_notes")
async def my_notes(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    cur.execute(
        "SELECT id, title, text FROM notes WHERE telegram_id = ?",
        (telegram_id,),
    )
    notes = cur.fetchall()
    await callback.answer()
    if not notes:
        await callback.message.answer("У вас пока нет заметок", reply_markup=main_menu())
        return

    text = "Ваши заметки\n\n"
    for note_id, title, note_text in notes:
        text += f"ID: {note_id}\n{escape(title)}\n{escape(note_text)}\n\n"
    await callback.message.answer(text, reply_markup=main_menu())


def note_buttons(notes, action):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=title, callback_data=f"{action}:{note_id}")]
            for note_id, title in notes
        ]
    )


async def get_user_notes(telegram_id):
    cur.execute("SELECT id, title FROM notes WHERE telegram_id = ?", (telegram_id,))
    return cur.fetchall()


@dp.callback_query(F.data == "edit_note")
async def edit_note(callback: CallbackQuery):
    notes = await get_user_notes(callback.from_user.id)
    await callback.answer()
    if not notes:
        await callback.message.answer("У вас нет заметок", reply_markup=main_menu())
        return
    await callback.message.answer(
        "Выберите заметку, которую хотите изменить",
        reply_markup=note_buttons(notes, "edit"),
    )


@dp.callback_query(F.data.startswith("edit:"))
async def choose_note_to_edit(callback: CallbackQuery, state: FSMContext):
    note_id = int(callback.data.split(":")[1])
    await state.update_data(note_id=note_id)
    await state.set_state(EditNote.text)
    await callback.answer()
    await callback.message.answer("Напишите новый текст заметки:")


@dp.message(EditNote.text)
async def save_edited_note(message: Message, state: FSMContext):
    data = await state.get_data()
    cur.execute(
        "UPDATE notes SET text = ? WHERE id = ? AND telegram_id = ?",
        (message.text, data["note_id"], message.from_user.id),
    )
    conn.commit()
    await state.clear()
    await message.answer("Заметка изменена", reply_markup=main_menu())



async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
