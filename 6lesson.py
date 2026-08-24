import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery, 
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
TOKEN="8652006388:AAFj2ygPuIFZhK7W46xQOE7Sb9JThvr4Dw0"
bot=Bot(token=TOKEN, default=DefaultBotProperties, parse_mode=ParseMode.HTML)
dp=Dispatcher()
conn=sqlite3.connect("courses.db")
cursor=conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT BULL
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_course(
        student_id INTEGER,
        course_id INTEGER,
        PRIMARY KEY(student_id, course_id)
        PRIMARY KEY(student_id)
            REFERNCES students(id),
        FOREIGN KEY (course_id)
            REFERENCES courses(id)
    )
""")
conn.commit()
def main_menu():