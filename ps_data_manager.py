import os
import pandas as pd
import logging
import sqlite3

from datetime import datetime
from users_manager import UsersModel, UsersСontroller
import ps_parser


#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_team(chat_id: int) -> dict:
    """
    Возвращает словарь {name:{omeda_id},}
    """
    uc = UsersСontroller()
    try:
        return uc.get_chat_users_and_omeda_id(chat_id)
    except Exception as e:
        logger.info(f"Проблемы с импортом игроков из БД: {e}")

def get_team_ps(chat_id: int) -> dict:
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
        team_ps = ps_parser.get_players_score_from_api(team)
        return team_ps
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