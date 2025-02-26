import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging

import ps_data_manager
import players

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


BASE_OMEDA_ADRESS = "https://omeda.city/players/"

def url_to_soup(url_address: str) -> object:
    """
    Create a BeautifulSoup object with attributes (response.text, 'html.parser)'
    :param url_address: url address of website
    :return: BeautifulSoup object
    """
    headers = {
        "Accept": '*/*',
        "User-Agent": UserAgent().random
    }
    resp = requests.get(url_address, headers=headers)

    return BeautifulSoup(resp.text, 'html.parser')

def get_players_score() -> dict[str, float]:
    """
    Get average ps value for players and return it as a dictioary with range 
    by score
    :return dictianary {player : average_score_value}
    """
    player_score : float = None
    players_score : dict[str, float] = {}

    for player, address in players.PLAYERS_ADRESSES.items():
        soup = url_to_soup(f"{BASE_OMEDA_ADRESS}{address}")
        try:
            player_score = float(soup.find('span', string="Average PS:"
            ).find_next_sibling('span').text)
        except AttributeError:
            player_score = 000.00
            logger.info(f"Data Parsing: The score for '{player}' is missing.")
        
        players_score[player.replace(' ','_')] = player_score
    
    logger.debug(players_score)
    logger.info("Data Parsing: Success")

    return players_score

def sort_players_by_score(player_score: dict[str, float]) -> dict[str, float]:
    """
    Sort dictionary by score. From high to low.
    """
    sorted_scores = dict(sorted(
        player_score.items(), key=lambda x: x[1], reverse=True))

    logger.debug(f"Sorted scores: {sorted_scores}")
    logger.info("Sorting players by score: Success")

    return sorted_scores


def make_score_prety(players_score : dict[str, float]) -> str:
    prety_player_score = ""
    players_score = sort_players_by_score(players_score)
    medals = ("🏆", "🥈", "🥉", "🧑‍🌾", "🧑‍🦯",)
    medals_counter = 0

    for player, score in players_score.items():
        if score < 100:
            score = "".join(("0", str(score)))

        prety_player_score += f"\n{score} | {medals[medals_counter]} | {player}"
        medals_counter += 1
    
    logger.debug(prety_player_score)
    logger.info("Make score pretty: Success")

    return prety_player_score
    
def main():
    #print(make_score_prety(get_players_score()))


    ps_data_manager.create_sql_database()

    ps_data_manager.write_df_to_sql_database(
        ps_data_manager.convert_ps_to_pd_dataframe(
            get_players_score()))


if __name__ == "__main__":
    main()
    