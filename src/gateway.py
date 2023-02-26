import telebot
import sqlite3
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot = telebot.TeleBot(os.getenv('TOKEN'))

conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()
