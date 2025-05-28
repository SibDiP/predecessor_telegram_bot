import os
import pandas as pd
import logging
import sqlite3
from ps_analitic_tools import Analitic

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from users_manager import UsersModel, UsersController
import ps_parser


#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
uc = UsersController()

async def player_ps_day_db_update():
    """
    Сборная функция для ежедневного обновления PS в датабазе.
    """
    
    users_dict = uc.get_users_and_omeda_id()
    # return dict[name:{'bd_id': int, 'omeda_id':str}] 
    new_ps = await ps_parser.get_players_score_from_api(users_dict)
    # return {name : {'bd_id': int, 'omeda_id':str, 'player_ps': float}

    #TODO место для записи ps в историю ps
    
    await uc.update_player_ps_day(new_ps)

    return None

def add_player_to_db(player_name: str, omeda_id: str, chat_id: int):
    uc.add_player(player_name, omeda_id, chat_id)
    return None

def get_player_ps(omeda_id: str) -> float:
    player_ps = ps_parser.get_player_ps_from_api(omeda_id)
    return player_ps

def get_team(chat_id: int) -> dict:
    """
    Возвращает словарь {name:{omeda_id},}
    """
    try:
        return uc.get_users_and_omeda_id(chat_id)
    except Exception as e:
        logger.info(f"Проблемы с импортом игроков из БД: {e}")

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
        return team_ps_dict

    except Exception as e:
        logger.info(f"Проблемы с парсингом PS: {e}")
        return {'Беда':0}

def sort_players_by_score(team_dict: dict[str, dict[str, str | float]]
) -> dict[str, dict[str, str | float]]:
    """
    Sort dictionary by score. From high to low.
    """
    try:
        team_dict_sorted_by_ps = (
            {k:v for k,v in sorted(
                team_dict.items(), key=lambda x: x[1]['player_ps'], reverse=True)
                }
            
            )

        logger.debug(f"Sorted scores: {team_dict_sorted_by_ps}")
        logger.info("Sorting players by score: Success")

        return team_dict_sorted_by_ps
    
    except Exception as e:
        logger.debug(f"Сортировка не удалась. Ошибка: {e}")
        return team_dict

def make_score_prety(team_dict: dict[str, dict[str, str | float]]) -> str:
    """
    Get PS dictionarry and return formatted string with players
    sorted by score amount.
    """
    OMEDA_PROFILE_ADRESS = "https://omeda.city/players/"
    pretty_player_score = ""
    # players_score = sort_players_by_score(players_score)
    medals = ("🏆", "🥈", "🥉", "🧑‍🌾", "🧑‍🦯",)
    medals_counter = 0
    
    for player, player_data in team_dict.items():
        logger.debug(f"MAKE PRETY:\nplayer:{player}, player_data:{player_data}")
        pretty_ps = f'{player_data['player_ps']:0>6.2f}'

        pretty_player_score += f'\n{pretty_ps} | {medals[medals_counter]} | <a href="{OMEDA_PROFILE_ADRESS}{player_data['omeda_id']}">{player}</a>' 
        medals_counter += 1                                             


    # for player, score in players_score.items():
    #     # number format xx.x -> 0xx.x0
    #     pretty_ps_score = f'{score:0>6.2f}'            

    #     pretty_player_score += f"\n{pretty_ps_score} | {medals[medals_counter]} | [{player}]({OMEDA_PROFILE_ADRESS}{player_data['omeda_id']}) "
    #     medals_counter += 1
    
    logger.debug(pretty_player_score)
    logger.info("Make score pretty: Success")

    return pretty_player_score 

async def players_ps_delta(chat_id:int) -> str | None:
    """
    Принимает chat_id
    Отдаёт отформатированный str ответ для чата, либо None если в БД ps_data 
    нет пользователей.

    Arg:
        chat_id: int
    
    Return:
        str - в случае успеха
        None - если для данного chat_id нет записей в ps_data.db
    """
    
    data_from_db = uc.get_users_and_omeda_id(chat_id)
    await ps_parser.get_players_last_match_ps(data_from_db)
    logger.debug(f"pdm, players_ps_delta(), словарь с last_match_ps: {data_from_db}")

    if is_chat_users_empty(data_from_db):
        return None

    new_data_from_api = sort_players_by_score(await get_team_ps(chat_id))

    logger.debug(f"DELTA_START: {data_from_db}")
    logger.debug(f"DELTA_END: {new_data_from_api}")

    delta = Analitic.difference_players_score_records(data_from_db, new_data_from_api)
    
    return delta

async def is_valid_omeda_id(omeda_id:str) -> bool:
    """
    Проверяет ответ omda API по заданному omeda_id.

    Arg:
    omeda_id: str 

    Return: bool 
    """

    if ps_parser.fetch_api_data(omeda_id) is None:
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



# Всё, что ниже, требует конкретного перелапачивания.

#PLAYERS_FOR_SQL = [k.replace(' ','_') for k in players.PLAYERS_ADRESSES.keys()]

# def convert_ps_to_pd_dataframe(players_score : dict[str, float]) -> pd.DataFrame:
#     """
#     Convert Player Score dictionary to pandas DataFrame with three
#     columns: id, Player, Player Score

#     return: pd.DataFrame
#     """

#     df = pd.DataFrame(data=players_score, index=[0])
#     df['date'] = datetime.now().strftime('%Y-%m-%d')
#     df = df.set_index('date')

#     logger.debug(f"\n{df.to_string()}")
#     logger.info("Create pandas DataFrame: Success")

#     return df

# def create_sql_database(sql_database : "str" = "ps_data.db") -> None:
#     """
#     Write pd.DataFrame object to .sqliete 
#     """
#     if os.path.isfile(sql_database):
#         logger.info(f"SQLite database creating: {sql_database} already exist")
#     else:
#         connection = sqlite3.connect(sql_database)
#         coursor = connection.cursor()
        
#         # Create table
#         coursor.execute(f'''
#         CREATE TABLE IF NOT EXISTS players_Score (
#         date TEXT PRIMARY KEY,
#         {", ".join([f"{player} REAL NOT NULL" 
#         for player in PLAYERS_FOR_SQL])}
#         )
#         ''')

#         # Save table
#         connection.commit()
#         logger.info(f"SQLite database {sql_database} creating: Success")
#         connection.close()

#     return None


# def write_df_to_sql_database(dataframe : pd.DataFrame, 
# sql_database : "str"="ps_data.db",
# sql_database_table : "str"="players_score") -> None:
    
#     if dataframe.empty:
#         logger.warning("DataFrame is empty. No data written to the database.")
#     else:
#         engine = create_engine(f'sqlite:///{sql_database}', echo=False)
#         try:
#             dataframe.to_sql(
#                 sql_database_table, 
#                 con=engine, 
#                 index_label="date",
#                 if_exists='append',)

#             logger.info(f"DataFrame writting to {sql_database}: Succsess")
#         except sqlalchemy.exc.IntegrityError:
#             logger.debug(f"write_df_to_sql_database: This date row already exist in {sql_database}")

#     return None


if __name__ == '__main__':
    pass