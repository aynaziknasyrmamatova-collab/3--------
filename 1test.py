
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

TOKEN = "8652006388:AAFeqcrQPs2GQ5sME_R3TcYf5c_LI8uATiA"
topics_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Python", callback_data="python")],
    [InlineKeyboardButton(text="SQL", callback_data="sql")],
    [InlineKeyboardButton(text="Linux", callback_data="linux")]
])

ttexts = {
    "python": "🐍 Python - один из самых востребованных языков программирования",
    "sql": "🗄 SQL - язык программирования для работы с базами данных.",
    "linux": "🐧 Linux - язык программирования, на котором написано большинство гаджетов."
}

dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(" Выберите тему:", reply_markup=topics_keyboard)

@dp.callback_query(F.data.in_(topic_texts.keys()))
async def process_topic_callback(callback: CallbackQuery):
    text = topic_texts[callback.data]
    await callback.message.answer(text)
    await callback.answer() 
async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
