import logging
import traceback

from utils.ps_analitic_tools import Analitic
from utils.users_manager import UsersModel, UsersController
import utils.ps_parser as ps_parser


logger = logging.getLogger(__name__)
uc = UsersController()

async def player_ps_day_db_update():
    """
    Сборная функция для ежедневного обновления PS в датабазе.
    """
    
    users_dict = uc.get_users_and_omeda_id()
    new_ps = await ps_parser.get_players_score_from_api(users_dict)
    
    await uc.update_player_ps_day(new_ps)

    return None

async def add_player_to_db(player_name: str, omeda_id: str, chat_id: int) -> None:
    """
    Добавляет нового игрока в базу данных. +парсит его PS

    Args:
        player_name (str): Никнейм игрока (макс. 25 символов)
        omeda_id (str): Omeda ID игрока (макс. 40 символов)
        chat_id (int): ID чата, к которому привязан игрок

    Returns:
        None: 

    Raises:
        ValueError: Если данные не соответствуют ограничениям
        Exeption: При прочих ошибках при добавлении в БД
    """

    await uc.add_player(player_name, omeda_id, chat_id)

    return None

def del_player_from_db(player_name: str, chat_id: int) -> None:
    """
    Удаляет игрока из базы данных.

    Args:
        player_name (str): Имя игрока
        chat_id (int): ID чата, к которому привязан игрок
    Returns:
        None:
    Raises:
        Exception: При ошибках во время удаления из БД
    """
    uc.del_player_from_db(player_name, chat_id)
    return None
    

def get_team(chat_id: int) -> dict:
    """
    Возвращает словарь {name:{omeda_id},}

    Args:
        chat_id (int): Идентификатор чата.
    Returns:
        dict[str, dict[str, str]]: Словарь {name: {omeda_id},}
    Raises:
        Exception: Если не удалось импортировать игроков из БД
    """
    return uc.get_users_and_omeda_id(chat_id)


async def get_team_ps(chat_id: int) -> dict:
    """
    Возвращает словарь {name: dict{'omeda_id':str, 'player_ps': int}}

        Args:
        chat_id (int): Идентификатор чата.

    Returns:
        dict[str, dict[str, str | float]]: Словарь {
        name: dict{'omeda_id':str, 'player_ps': int}}

    Raises:
        Exception: Если не удалось cпарсить данные с API omeda
    """
    team = get_team(chat_id)

    try:
        team_ps_dict = await ps_parser.get_players_score_from_api(team)
        logger.debug(f"team_ps_dict: {team_ps_dict}")
        logger.info(f"chat_id: {chat_id}. Получили данные о PS игроков из БД")
        return team_ps_dict

    except Exception as e:
        logger.error(f"Проблемы с парсингом PS: get_team_ps, {e}")
        logger.error(traceback.format_exc())
        return {'Беда':0}

def sort_players_by_score(team_dict: dict[str, dict[str, str | float]]
) -> dict[str, dict[str, str | float]]:
    """
    Сортирует игроков по PS от большего к меньшему

    Args:
        team_dict (dict[str, dict[str, str | float]]): Словарь {
        name: dict{'omeda_id':str, 'player_ps': int}}
    Returns:
        dict[str, dict[str, str | float]]: Словарь {
        name: dict{'omeda_id':str, 'player_ps': int}}
    Raises:
        Exception: При ошибках во время сортировки
    """
    try:
        team_dict_sorted_by_ps = (
            {k:v for k,v in sorted(
                team_dict.items(), key=lambda x: x[1]['player_ps'], reverse=True)
                }
            )
        logger.debug(f"Сортированные значения: {team_dict_sorted_by_ps}")
        logger.info("Сортировка игроков по PS: Success")

        return team_dict_sorted_by_ps
    
    except Exception as e:
        logger.debug(f"Сортировка не удалась. Ошибка: {e}")
        return team_dict


async def get_start_and_end_users_dict_for_delta(chat_id:int
) -> tuple[dict, dict] | None:
    """
    Возвращает словари {name: {omeda_id},} для старых и новых данных

    Args:
        chat_id (int): Идентификатор чата.
    Returns:
        tuple[dict, dict] | None: Словарь {name: {omeda_id},} для старых и новых данных
    Raises:
        Exception: При ошибках во время парсинга PS
    """

    data_from_db = uc.get_users_and_omeda_id(chat_id)
    if is_chat_users_empty(data_from_db):
        return None

    new_data_from_api = sort_players_by_score(await get_team_ps(chat_id))

    logger.debug(f"DELTA_START: {data_from_db}")
    logger.debug(f"DELTA_END: {new_data_from_api}")

    return (data_from_db, new_data_from_api)

async def players_ps_delta(chat_id:int) -> str | None:
    """
    Возвращает строку с дельтой PS игроков
    Args:
        chat_id (int): Идентификатор чата.
    Returns:
        str | None: Строка с дельтой PS игроков
    Raises:
        Exception: При ошибках во время парсинга PS и/или в БД
    """
    
    delta = Analitic.difference_players_score_records(
        *await get_start_and_end_users_dict_for_delta(chat_id))
    
    return delta

async def is_valid_omeda_id(omeda_id:str) -> bool:
    """
    Проверяет ответ omda API по заданному omeda_id.

    Arg:
    omeda_id: str 

    Return: bool 
    """

    if await ps_parser.fetch_api_data(omeda_id) is None:
        return False
    else:
        return True

def is_valid_name(name:str) -> bool:
    """
    Проверяет длинну введённого никнейма. Может быть не более 25 символов
    (ограничение ДБ в UsersModel)

    Arg:
    name:str 

    Return: bool
    """

    if len(name) > UsersModel.NAME_LEN:
        return False
    else:
        return True

def is_chat_users_empty(users_dict: dict) -> bool:
    """
    Проверяет не пуст ли словарь. True - пустой, False - пустой
    """

    if not users_dict:
        return True
    else:
        False


if __name__ == '__main__':
    pass