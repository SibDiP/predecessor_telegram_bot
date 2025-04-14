import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import os
from dotenv import load_dotenv
import ps_parser
from ps_analitic_tools import Analitic

load_dotenv()

TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=TG_TOKEN)
# Диспетчер 
# объект, занимающийся получением апдейтов от Telegram с 
# последующим выбором хэндлера для обработки принятого апдейта.
dp = Dispatcher()

# Хэндлер на команду /start
# асинхронная функция, которая получает от диспетчера/роутера 
# очередной апдейт и обрабатывает его.
#
# Апдейт — любое событие из этого списка: 
# сообщение, редактирование сообщения, 
# колбэк, инлайн-запрос, платёж, добавление 
# бота в группу и т.д. 

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

# Хэндлер на команду /ps
@dp.message(Command("ps"))
async def cmd_ps(message: types.Message):
    await message.answer(f"{ps_parser.make_score_prety(ps_parser.get_players_score_from_api())}")

@dp.message(Command("ps_rec_start"))
async def cmd_ps_rec_start(message: types.Message):
    await message.answer(
        Analitic.setter_players_score_start(
            ps_parser.get_players_score_from_api()))

@dp.message(Command("ps_rec_end"))
async def cmd_ps_rec_end(message: types.Message):
    await message.answer(
        Analitic.setter_players_score_end(
            ps_parser.get_players_score_from_api()))

@dp.message(Command("ps_rec_result"))
async def cmd_ps_rec_result(message: types.Message):
    await message.answer(
        Analitic.difference_players_score_records())

# Хэндлер на команду /test2
async def cmd_test2(message: types.Message):
    await message.reply("Test 2")


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

# Тело бота

if __name__ == "__main__":
    # Commited until it's done
    loop = asyncio.get_event_loop()
    #loop.run_in_executor(None, ps_parser.schedule_every_day)

    loop.run_until_complete(main())

    #asyncio.run(main())