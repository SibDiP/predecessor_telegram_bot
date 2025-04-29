import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
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

# @dp.message(Command("add_player"))
# async def cmd_start(message: types.Message):
#     chat_id = message.chat.id
#     await message.answer("Hello!")

from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# 1. Определяем состояния FSM (Finite State Machine)
class AddPlayerStates(StatesGroup):
    """
    Класс состояний для процесса добавления игрока.
    Каждое состояние соответствует этапу диалога.
    """
    waiting_for_name = State()      # Ожидание ввода никнейма
    waiting_for_omeda_id = State()  # Ожидание ввода Omeda ID

# 2. Хендлер команды /add_player
@dp.message(Command("add_player"))
async def cmd_add_player(message: types.Message, state: FSMContext):
    """
    Обработчик команды /add_player.
    Инициализирует процесс добавления игрока.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст состояния FSM
    """
    # Сохраняем идентификаторы пользователя и чата
    await state.update_data(
        user_id=message.from_user.id,  # Уникальный ID пользователя
        chat_id=message.chat.id        # ID чата (личного или группового)
    )
    
    # Создаем клавиатуру с кнопкой отмены
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="❌ Отмена"))
    
    # Запрашиваем никнейм игрока
    await message.answer(
        "Введите никнейм игрока:",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )
    # Устанавливаем первое состояние
    await state.set_state(AddPlayerStates.waiting_for_name)

# 3. Хендлер для обработки никнейма
@dp.message(AddPlayerStates.waiting_for_name, F.text != "❌ Отмена")
async def process_player_name(message: types.Message, state: FSMContext):
    """
    Обрабатывает введенный никнейм игрока.
    Проверяет, что сообщение от того же пользователя, который начал процесс.
    
    Args:
        message: Объект сообщения с никнеймом
        state: Контекст состояния FSM
    """
    # Получаем сохраненные данные
    data = await state.get_data()
    
    # Проверяем, что сообщение от того же пользователя
    if message.from_user.id != data['user_id']:
        await message.answer("Пожалуйста, дождитесь завершения текущего процесса.")
        return
    
    # Сохраняем никнейм и запрашиваем Omeda ID
    await state.update_data(player_name=message.text)
    
    await message.answer(
        "Введите Omeda ID игрока (https://omeda.city/players/{omeda_id}):",
        reply_markup=types.ReplyKeyboardRemove()  # Убираем клавиатуру
    )
    # Переходим к следующему состоянию
    await state.set_state(AddPlayerStates.waiting_for_omeda_id)

# 4. Хендлер для обработки Omeda ID
@dp.message(AddPlayerStates.waiting_for_omeda_id, F.text != "❌ Отмена")
async def process_omeda_id(message: types.Message, state: FSMContext):
    """
    Обрабатывает введенный Omeda ID и завершает процесс добавления.
    
    Args:
        message: Объект сообщения с Omeda ID
        state: Контекст состояния FSM
    """
    # Получаем все сохраненные данные
    data = await state.get_data()
    
    # Проверяем пользователя
    if message.from_user.id != data['user_id']:
        await message.answer("Пожалуйста, не мешайте другим игрокам.")
        return
    
    # Получаем сохраненные значения
    player_name = data['player_name']
    omeda_id = message.text
    chat_id = data['chat_id']
    
    try:
        # Добавляем игрока в базу данных
        ps_data_manager.add_player(player_name, omeda_id, chat_id)
        
        # Отправляем подтверждение
        await message.answer(
            f"Игрок {player_name} успешно добавлен в команду!",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except Exception as e:
        await message.answer(
            f"Ошибка при добавлении игрока: {str(e)}",
            reply_markup=types.ReplyKeyboardRemove()
        )
    finally:
        # Всегда очищаем состояние
        await state.clear()

# 5. Хендлер для отмены операции
@dp.message(F.text == "❌ Отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Обработчик отмены операции.
    """
    data = await state.get_data()
    if message.from_user.id == data.get('user_id'):
        await message.answer(
            "Добавление игрока отменено.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.clear()



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