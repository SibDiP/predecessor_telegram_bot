import asyncio
import logging
from aiogram import Bot, Dispatcher, types ,F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os
from dotenv import load_dotenv
import ps_parser
from ps_analitic_tools import Analitic
import ps_data_manager

load_dotenv()

TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
LOG_LVL = getattr(logging, os.getenv("LOGGING_MODE"))

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=LOG_LVL)
logger = logging.getLogger(__name__)

ps_data_manager.create_sql_database()

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

# Хэндлер на команду /ps
@dp.message(Command("ps"))
async def cmd_ps(message: types.Message):
    await message.answer(f"{ps_parser.make_score_prety(ps_parser.get_players_score_from_api())}")

@dp.message(Command("ps_rec_start"))
async def cmd_ps_rec_start(message: types.Message):
    await message.answer(
        Analitic.setter_players_score_start(
            ps_parser.get_players_score_from_api()))

@dp.message(Command("ps_rec_result"))
async def cmd_ps_rec_result(message: types.Message):
    await message.answer(
        Analitic.difference_players_score_records())

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

# add_player логика

class AddPlayerStates(StatesGroup):
    """
    Класс состояний для этапов добавления игрока
    """
    waiting_for_name = State() 
    waiting_for_omeda_id = State()

def get_cancel_inline_keyboard():
    """Создает inline-клавиатуру с кнопкой отмены"""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="cancel_add_player")
    return builder.as_markup()

@dp.message(Command("add_player"))
async def cmd_add_player(message: types.Message, state: FSMContext):
    """
    Инициализация процесса добавления игрока в БД
    """
    await state.update_data(
        user_id=message.from_user.id,
        chat_id=message.chat.id
    )

    await message.answer(
        "Введите никнейм:",
        reply_markup=get_cancel_inline_keyboard()
    )
    await state.set_state(AddPlayerStates.waiting_for_name)

@dp.message(AddPlayerStates.waiting_for_name)
async def process_add_player_name(message: types.Message, state: FSMContext):
    """
    Обрабатывает никнейм.
    Проверяет пользователя
    """
    data = await state.get_data()

    if message.from_user.id != data['user_id']:
        await message.answer("Подождите завершения процесса.")
        return
    
    await state.update_data(player_name=message.text)

    await message.answer(
        "Введите Omeda ID игрока (https://omeda.city/players/{omeda_id}):",
        reply_markup=get_cancel_inline_keyboard()
    )
    await state.set_state(AddPlayerStates.waiting_for_omeda_id)

@dp.message(AddPlayerStates.waiting_for_omeda_id)
async def process_add_player_omeda_id(message: types.Message, state: FSMContext):
    """
    Обрабатывает omeda_id,
    проверяет пользователя,
    завершает процесс добавления нового игрока в БД
    """
    data = await state.get_data()

    if message.from_user.id != data['user_id']:
        await message.answer("Подождите завершения процесса.")
        return
    
    player_name = data['player_name']
    omeda_id = message.text
    chat_id = data['chat_id']

    try:
        ps_data_manager.add_player(player_name, omeda_id, chat_id)
        await message.answer(
            f"Игрок {player_name} успешно добавлен в команду!",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except Exception as e:
        await message.answer(
            f"Ошибка при добавлении игрока: {str(e)}"
        )
    finally:
        await state.clear()

@dp.callback_query(F.data == "cancel_add_player")
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик отмены операции через inline-кнопку
    """
    data = await state.get_data()
    if callback.from_user.id == data.get('user_id'):
        await callback.message.edit_text(
            "Добавление игрока отменено",
            reply_markup=None
        )
        await state.clear()
    await callback.answer()

async def main():
    await dp.start_polling(bot)

# Тело бота

if __name__ == "__main__":
    # Commited until it's done
    loop = asyncio.get_event_loop()
    #loop.run_in_executor(None, ps_parser.schedule_every_day)

    loop.run_until_complete(main())

    #asyncio.run(main())