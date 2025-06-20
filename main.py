"""
Скрипт Telegram-бота для отслеживания показателей игроков.

Этот скрипт настраивает Telegram-бота с командами для:
    Отслеживания ежедневных показателей эффективности игроков
    Добавления и удаления игроков из базы данных
    Получения изменений показателей эффективности для участников чата

Ключевые особенности:
    Использует aiogram для работы Telegram-бота
    Реализует state machines для управления игроками
    Выполняет ежедневное обновление данных об эффективности игроков
    Обеспечивает обработку ошибок и логирование
    """
import os
import logging
import traceback

from dotenv import load_dotenv
import aiocron
import asyncio
from aiogram import Bot, Dispatcher, types ,F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm.exc import NoResultFound
from aiogram.enums import ParseMode 

import utils.ps_data_manager as pdm


load_dotenv()

TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Включаем логирование, чтобы не пропустить важные сообщения
LOG_LVL = getattr(
    logging, os.getenv("LOGGING_MODE", "WARNING").upper(), logging.WARNING)
logging.basicConfig(level=LOG_LVL)
logger = logging.getLogger(__name__)

# Объект бота
bot = Bot(token=TG_TOKEN)

# Диспетчер 
# объект, занимающийся получением апдейтов от Telegram с 
# последующим выбором хэндлера для обработки принятого апдейта.
dp = Dispatcher()

# Хэндлер на команду 
# асинхронная функция, которая получает от диспетчера/роутера 
# очередной апдейт и обрабатывает его.

# Апдейт — любое событие из этого списка: 
# сообщение, редактирование сообщения, 
# колбэк, инлайн-запрос, платёж, добавление 
# бота в группу и т.д. 

@aiocron.crontab('* 4 * * *')
async def daily_update():
    """
    Ежедневный апдейт значений player_ps_day в ps_data.db
    """
    try:
        await pdm.player_ps_day_db_update()
    
    except Exception as e:
        logger.error(f"daily_update(): {e}")

@dp.message(Command("delta"))
async def cmd_delta(message: types.Message):
    """
    Возвращает сообщение c измененеием PS для участников чата
    """
    try:
        delta_data = await pdm.players_ps_delta(message.chat.id)
        if delta_data is None:
            await message.answer("Нет зарегистрированных пользователей. Используйте команду /add_player")
            return

        await message.answer((delta_data),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True)
    
    except Exception as e:
        logger.error(f"cmd_delta(): {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        await message.answer("Ошибка дельты PS. Убедитесь, что добавлен хотя бы один игрок")

class DelPlayerStates(StatesGroup):
    """
    Класс состояний для этапов удаления игрока
    """
    waiting_for_name = State()

# Удаление игрока из БД
@dp.message(Command("del_player"))
async def cmd_del_player(message: types.Message, state: FSMContext, bot: Bot):
    """
    Удаляет игрока с указанными name + сграбленным chat_id 
    """
    await state.update_data(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        messages=[]
    )

    msg = await message.answer(
        "Введите никнейм удаляемого игрока:",
        reply_markup=get_cancel_inline_keyboard()
    )
    
    await state.update_data(messages=[msg.message_id])
    await state.set_state(DelPlayerStates.waiting_for_name)    

@dp.message(DelPlayerStates.waiting_for_name)
async def process_del_player_name(
    message: types.Message, state: FSMContext, bot: Bot):
    """
    Обрабатывает никнейм и завершает процесс удаления игрока.
    """
    data = await state.get_data()

    if message.from_user.id != data['user_id']:
       await message.answer("Подождите завершения процесса добавления игрока")
       return
    
    # Удаляем кнопку из предыдущего сообщения
    await remove_inline_buttons(message.chat.id, data['messages'], bot)
    
    player_name = message.text.strip()
    chat_id = data['chat_id']

    try:
        pdm.del_player_from_db(player_name, chat_id)
        
        await message.answer(
            f"Игрок {player_name} успешно удалён из команды!"
        )

    except NoResultFound:
        await message.answer(
            f"Игрок {player_name} не найден в базе"
        )

    except Exception as e:
        logger.error(f"process_del_player_name: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        await message.answer("Ошибка при удалении игрока")

    finally:
        await state.clear()

# Добавление игрока в БД
class AddPlayerStates(StatesGroup):
    """
    Класс состояний для этапов добавления игрока
    """
    waiting_for_name = State()
    waiting_for_omeda_id = State()

def get_cancel_inline_keyboard():
    """Создает inline-клавиатуру c кнопкой отмены"""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="cancel_inline_button")
    return builder.as_markup()


@dp.callback_query(F.data == "cancel_inline_button")
async def cancel_add_player_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обработчик отмены операции
    """
    data = await state.get_data()
    
    if callback.from_user.id == data.get('user_id'):
        # Удаляем все инлайн-кнопки
        await remove_inline_buttons(callback.message.chat.id, data['messages'], bot)
        
        await callback.message.edit_text(
            "Операция отменена",
            reply_markup=None
        )
        await state.clear()
    
    await callback.answer() # подтверждение

async def remove_inline_buttons(chat_id: int, message_ids: list[int], bot: Bot):
    """Удаляет инлайн-кнопки из сообщений"""
    for msg_id in message_ids:
        try:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=msg_id,
                reply_markup=None # удаляет все инлайн сущности
            )
        except Exception:
            pass

@dp.message(Command("add_player"))
async def cmd_add_player(message: types.Message, state: FSMContext, bot: Bot):
    """
    Инициализация процесса добавления игрока в БД
    """
    await state.update_data(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        messages=[]
    )

    msg = await message.answer(
        "Введите никнейм:",
        reply_markup=get_cancel_inline_keyboard()
    )
    
    await state.update_data(messages=[msg.message_id])
    await state.set_state(AddPlayerStates.waiting_for_name)

@dp.message(AddPlayerStates.waiting_for_name)
async def process_add_player_name(message: types.Message, state: FSMContext, bot: Bot):
    """
    Обрабатывает никнейм и запрашиваем omeda_id
    """
    data = await state.get_data()

    if message.from_user.id != data['user_id']:
       await message.answer("Подождите завершения процесса добавления игрока")
       return
    
    # Удаляем кнопку из предыдущего сообщения
    await remove_inline_buttons(message.chat.id, data['messages'], bot)
    
    if not pdm.is_valid_name(message.text.strip()):
        await message.answer("Никнейм может содержать не более 25 символов")
        return

    await state.update_data(player_name=message.text.strip())
    
    msg = await message.answer(
        "Введите Omeda ID игрока (https://omeda.city/players/{omeda_id}):",
        reply_markup=get_cancel_inline_keyboard()
    )
    
    await state.update_data(messages=data['messages'] + [msg.message_id])
    await state.set_state(AddPlayerStates.waiting_for_omeda_id)

@dp.message(AddPlayerStates.waiting_for_omeda_id)
async def process_add_player_omeda_id(message: types.Message, state: FSMContext, bot: Bot):
    """
    Завершает процесс добавления игрока
    """
    data = await state.get_data()

    if not await pdm.is_valid_omeda_id(message.text):
        await message.answer("Не корректный Omeda_id. Введите корректный или отмените операцию")
        return
    
    # Удаляем все инлайн-кнопки
    await remove_inline_buttons(message.chat.id, data['messages'], bot)
    
    player_name = data['player_name']
    omeda_id = message.text.strip()
    chat_id = data['chat_id']

    try:
        # Ваш метод добавления в БД
        await pdm.add_player_to_db(player_name, omeda_id, chat_id)
        
        await message.answer(
            f"Игрок {player_name} успешно добавлен в команду!"
        )
    except Exception as e:
        logger.error(f"process_add_player_omeda_id: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        #TODO добавить валидацию на omeda_id и выдать соответсвующую ошибку в чат
        await message.answer("Ошибка при добавлении игрока")
    finally:
        await state.clear()

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


# Тело бота
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.info(f"Бот остановлен: {e}")
