import requests

#from bs4 import BeautifulSoup
#from fake_useragent import UserAgent
import logging
import schedule
from time import sleep

import ps_data_manager
import users_manager # users_manager тепреь

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


BASE_OMEDA_ADRESS = "https://omeda.city/players/"

def get_players_score_from_api(
    team_dict: dict[str, dict[str, str]]
    ) -> dict[str, dict[str, str | float]]:
    """
    Get average ps value for players from API object and return it 
    as a dictioary with range by score
    :team_dict: dict[name:{'omeda_id':str}]
    :return dictianary {name : {'omeda_id':str, 'player_ps': float}
    """
    DATA_FOR_EXTRACTION = "avg_performance_score"
    
    for player, player_info in team_dict.items():
        try:
            response = requests.get(f"{BASE_OMEDA_ADRESS}{player_info['omeda_id']}/statistics.json")
            if response.status_code == 200:
                api_data = response.json()
                logger.debug(f"API data for {player}:\n{api_data}")
                logger.info(f"Get API data for {player}: Success")

                player_ps = round(api_data[DATA_FOR_EXTRACTION], 2)
                player_info['player_ps'] = player_ps

            else:
                logger.info(f"Data extraction: API/GET erorr {response.status_code}")   
        
        except Exception as e:
            logger.info(f"Ошибка парсинга, {player}. {e}")
            player_ps = 0

    logger.debug(f"Team_dict: {team_dict}")
    logger.info("Data Parsing: Success")

    return team_dict

# TODO: всё что ниже переделать

def ps_from_api_to_db():
    ps_data_manager.write_df_to_sql_database(
    ps_data_manager.convert_ps_to_pd_dataframe(
        get_players_score_from_api()))
    logger.info("Today data saving in db: Success")

def schedule_every_day():
    # TODO add condition for longer sleep time
    schedule.every().day.at("21:50").do(ps_from_api_to_db)
    while True:
        schedule.run_pending()
        logger.debug("Чекнул")
        sleep(50)

# def get_players_score_form_bs() -> dict[str, float]:
#     """
#     LEGACY FUNCTION! REPLACED BY get_players_score_from_api
#     Get average ps value for players from beautifulSoup object and return it 
#     as a dictioary with range by score
#     :return dictianary {player : average_score_value}
#     """
#     player_score : float = None
#     players_score : dict[str, float] = {}

#     for player, address in players.PLAYERS_ADRESSES.items():
#         soup = url_to_soup(f"{BASE_OMEDA_ADRESS}{address}")
#         try:
#             player_score = float(soup.find('span', string="Average PS:"
#             ).find_next_sibling('span').text)
#         except AttributeError:
#             player_score = 000.00
#             logger.info(f"Data Parsing: The score for '{player}' is missing.")
        
#         players_score[player.replace(' ','_')] = player_score
    
#     logger.debug(players_score)
#     logger.info("Data Parsing: Success")

#     return players_score

# def url_to_soup(url_address: str) -> object:
#     """
#     LEGACY FUNCTION! REPLACED BY get_players_score_from_api
#     Create a BeautifulSoup object with attributes (response.text, 'html.parser)'
#     :param url_address: url address of website
#     :return: BeautifulSoup object
#     """
#     headers = {
#         "Accept": '*/*',
#         "User-Agent": UserAgent().random
#     }
#     resp = requests.get(url_address, headers=headers)

#     return BeautifulSoup(resp.text, 'html.parser')

def main():
    #schedule_every_day()
    #Analitic.players_score_recorder_start(get_players_score_from_api())
    get_players_score_from_api()



if __name__ == "__main__":
    main()
    