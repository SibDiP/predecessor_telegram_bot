import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


# Traced players. {nik_name : id}
PLAYERS_ADRESSES = {
    "Evvec" : "d6f5c363-6550-4af2-a84e-2d8e68e0010b",
    "good boy 69 69" : "f78da535-daad-4b6d-a151-aafc9eeb6d0c",
    "PowerSobaka9000" : "d721a45e-c57a-4b8e-b866-8179d1365dfa",
    "sibdip" : "22721c84-9d9e-4bdc-a6d6-758806afa0b1",
    "styxara" : "304a359b-2329-4ea7-8007-095e292f382e",
    }
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

    for player, address in PLAYERS_ADRESSES.items():
        soup = url_to_soup(f"{BASE_OMEDA_ADRESS}{address}")
        try:
            player_score = float(soup.find('span', string="Average PS:"
            ).find_next_sibling('span').text)
        except AttributeError:
            player_score = 000.00
        
        players_score[player] = player_score
    
    return players_score

def sort_players_by_score(player_score: dict[str, float]) -> dict[str, float]:
    """
    Sort dictionary by score. From high to low.
    """
    sorted_scores = dict(sorted(
        player_score.items(), key=lambda x: x[1], reverse=True))
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
    
    return prety_player_score
    
def main():
    print(make_score_prety(get_players_score()))

if __name__ == "__main__":
    main()
    