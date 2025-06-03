import logging
import traceback

import ps_parser

logger = logging.getLogger(__name__)

class Analitic:


    @staticmethod
    def difference_players_score_records(
        data_start: dict[str, dict[str, str| int |float]],
        data_end: dict[str, dict[str, str| int |float]],
    ) -> str:

        result_string = ""
        up_down_neutral_emoji = ("🟢","🔴","🟡")
        compare_index : int = None
        compare_difference : float = None
        #BASE_OMEDA_ADRESS = "https://omeda.city/players/"

        # loop through Analitic.players_score_end
        for player, player_data in data_end.items():
            
            try:
                current_ps = data_start[player]['player_ps_day']
                next_ps = player_data['player_ps_day']
                last_match_ps = player_data['player_ps']
            except Exception as e:
                logger.error(f"difference_players_score_records: {e}")
                logger.error(traceback.format_exc())
            
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
                f'''<a href="{ps_parser.BASE_OMEDA_ADRESS}{player_data['omeda_id']}">{player[:13]}</a>\n'''
                )
        return  result_string

def main():
    pass


if __name__ == "__main__":
    main()