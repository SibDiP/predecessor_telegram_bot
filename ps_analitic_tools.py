from typing import Optional
import logging

import ps_parser

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Analitic:
    players_score_start : dict[str, float] = {}
    players_score_end : dict[str, float] = {}

    @staticmethod
    def setter_players_score_start(players_score : dict [str, float]) -> str:
        """
        Get current play score data and save it as start point for recording.
        """
        Analitic.players_score_start = players_score
        
        return "Стартовый PS записан"

    @staticmethod
    def setter_players_score_end(players_score : dict [str, float]) -> str:
        """
        Get current play score data and save it as end point for recording
        """
        return_options = ("Начальный PS отсуствует", "Конечный PS записан")
        if not Analitic.players_score_start:
            return_option = 0
        else:
            Analitic.players_score_end = players_score
            return_option = 1

        return return_options[return_option]

    @staticmethod
    def clear_players_score_records() -> None:
        """
        Reset players_score_start and players_score_end
        """
        Analitic.players_score_start, Analitic.players_score_end = None, None

    # @staticmethod
    # def is_ps_records_written() -> str:
    #     return_options = (
    #         "Начальный PS отсутсвует",
    #         "Конечный PS отсутсвует",
    #         "Записи PS отсутсвуют", "")
        

    @staticmethod
    def difference_players_score_records(
        data_start: dict[str, dict[str, str| int |float]],
        data_end: dict[str, dict[str, str| int |float]],
    ) -> str:

        result_string = ""
        up_down_neutral_emoji = ("🟢","🔴","🟡")
        compare_index : int = None
        compare_difference : float = None
        BASE_OMEDA_ADRESS = "https://omeda.city/players/"

        # loop through Analitic.players_score_end
        for player, player_data in data_end.items():
            logger.debug(f"difference_players_score_records, data_start: {data_start}")
            current_ps = data_start[player]['player_ps_day']
            next_ps = player_data['player_ps']
            last_match_ps = data_start[player]['last_match_ps']
            
            compare_difference = abs(next_ps - current_ps)

            if next_ps > current_ps:
                compare_index = 0
            elif next_ps < current_ps:
                compare_index = 1
            elif next_ps == current_ps:
                compare_index = 2


            #formatted_str = f"{number:06.2f}"
            result_string += (
                f"{next_ps:0>6.2f} | " +
                f"{up_down_neutral_emoji[compare_index]} {compare_difference:0>4.2f} | " +
                f"{last_match_ps:0>6.2f} | " +
                f'''<a href="{BASE_OMEDA_ADRESS}{player_data['omeda_id']}">{player[:13]}</a>\n'''
                )
        return  result_string

def make_score_prety(players_score : dict[str, float]) -> str:
    prety_player_score = ""
    players_score = ps_parser.sort_players_by_score(players_score)
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
    pass


if __name__ == "__main__":
    main()