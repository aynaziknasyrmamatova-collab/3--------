import asyncio
from aiogram import Bot,Dispatcher,F
from aiogram.types import Message,CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
TOKEN="8652006388:AAFeqcrQPs2GQ5sME_R3TcYf5c_LI8uATiA"
bot=Bot(token=TOKEN)
dp=Dispatcher()
@dp.message(F.text=="/start")
# async def start(message:Message):
#     keyboard=InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text="Аргетина",
#                     callback_data="Аргентина"

#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text="Испания",
#                     callback_data="Испания"

#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text="Португалия"
#                     callback_data="Португалия"
#                 )
#             ]
#         ]
#     )
#     await message.answer(
#         "Кто выиграл чемпионат мира 2026?"
#         reply_markup=keyboard
#     )
# @dp.callback_query(F.data=="Испания")
# async def correct_answer(callback:CallbackQuery):
#     await callback.answer("Правильно!")
#     await callback.message.answer(
#         "Правильный ответ! Испания выиграл Чемпионат мира 2026"
#     )
# @dp.callback_query(F.data=="аргентина")
# async def argentina(callback:CallbackQuery):
#     await callback.answer("Неправильно")
#     await callback.message.answer(
#         "Нет. Испания выиграла чемпионат мира 2026"
#     )
# @dp.callback_query(F.data=="Португалия")
# async def portugal(callback:CallbackQuery):
#     await callback.answer("Неправильно")
#     await callback.message.answer(
#         "Нет. Испания выиграла чемпионат мира 2026"
#     )
# async def main():
#     await dp.start_polling(bot)
# if __name__=="__main__":
#     asyncio.run(main())
# async def start(message:Message):
#     keyboard=InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text="овощь",
#                     callback_data="овощь"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text="фрукт",
#                     callback_data="фрукт"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text="ягода",
#                     callback_data="ягода"
#                 )
#             ]
#         ]
#     )
#     await message.answer(
#         "Какого вида яблоко?",
#         reply_markup=keyboard
#     )
# @dp.callback_query(F.data=="фрукт")
# async def correct_answer(callback:CallbackQuery):
#     await callback.answer("правильно!")
#     await callback.message.answer(
#         "правильный ответ! Яблоко это фрукт"
#     )
# @dp.callback_query(F.data=="ягода")
# async def berry(callback:CallbackQuery):
#     await callback.answer("Неправильно")
#     await callback.message.answer(
#         "Нет. Яблоко это фрукт"
#     )
# @dp.callback_query(F.data=="овощь")
# async def vegetable(callback:CallbackQuery):
#     await callback.answer("Неправильно")
#     await callback.message.answer(
#         "Нет. Яблоко это фрукт"
#     )
# async def main():
#     await dp.start_polling(bot)
# if __name__=="__main__":
#     asyncio.run(main())
async def start(message:Message):
    keyboard=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Железный человек",
                    callback_data="Железный человек"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Бэтмен",
                    callback_data="Бэтмен"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Супер-Женщина",
                    callback_data="Супер-Женщина"
                )
            ]
        ]
    )
    await message.answer(
        "Кто входит во вселенную Марвел?",
        reply_markup=keyboard
    )
@dp.callback_query(F.data=="Железный человек")
async def correct_answer(callback:CallbackQuery):
    await callback.answer("правильно!")
    await callback.message.answer(
        "Правильный ответ! железный человек входит во вселенную Марвел"
    )
@dp.callback_query(F.data=="Бэтмен")
async def batman(callback:CallbackQuery):
    await callback.answer("Неправильно")
    await callback.message.answer(
        "Нет. железный человек входит в Марвел"
    )
@dp.callback_query(F.data=="Супер-Женщина")
async def superwoman(callback:CallbackQuery):
    await callback.answer("Неправильно")
    await callback.message.answer(
        "Нет. железный человек входит во вселенную Марвел"
    )
async def main():
    await dp.start_polling(bot)
if __name__ =="__main__":
    asyncio.run(main())