import asyncio
import json
import os

from configparser import ConfigParser
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from telebot.async_telebot import AsyncTeleBot
from app.db import get_payments

API_TOKEN = os.getenv("API_TOKEN")
DATABASE_URI = os.getenv("DATABASE_URI")


bot = AsyncTeleBot(API_TOKEN)


def get_client():
    return AsyncIOMotorClient(DATABASE_URI)
    

@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    client = get_client()
    

    text = message.text

    try:
        data = dict(json.loads(text))
        dt_from = datetime.fromisoformat(data['dt_from'])
        dt_to = datetime.fromisoformat(data['dt_upto'])
        result = await get_payments(dt_from, dt_to, data["group_type"], client)
        await bot.send_message(message.chat.id, result)
    except:
        await bot.send_message(message.chat.id, {})


asyncio.run(bot.polling())