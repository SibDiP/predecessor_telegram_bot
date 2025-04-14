from typing import Optional

class Analitic:
    players_score_start : dict[str, float] = {}
    players_score_end : dict[str, float] = {}

    @staticmethod
    def setter_players_score_start(players_score : dict [str, float]) -> None:
        """
        Get current play score data and save it as start point for recording.
        """
        Analitic.players_score_start = players_score
        
        return "Стартовый PS записан"

    @staticmethod
    def setter_players_score_end(players_score : dict [str, float]) -> None:
        """
        Get current play score data and save it as end point for recording
        """
        Analitic.players_score_end = players_score

        return "Конечный PS записан"

    @staticmethod
    def clear_players_score_records() -> None:
        """
        Reset players_score_start and players_score_end
        """
        Analitic.players_score_start, Analitic.players_score_end = None, None
    
    @staticmethod
    # TODO! - works, bud awful
    def difference_players_score_records(
        data_start: Optional[dict[str, float]] = None,
        data_end: Optional[dict[str, float]] = None,
    ) -> str:
        if data_start is None:
            data_start = Analitic.players_score_start
        if data_end is None:
            data_end = Analitic.players_score_end

        result_string = ""
        up_down_neutral_emoji = ("📈","📉","➖")
        compare_signs = ("+", "-", " ")
        compare_index : int = None
        compare_difference : float = None


        # loop throug data_end
        for player, score in data_end.items():
            compare_difference = abs(data_end[player] - data_start[player])

            if data_end[player] > data_start[player]:
                compare_index = 0
            elif data_end[player] < data_start[player]:
                compare_index = 1
            elif data_end[player] == data_start[player]:
                compare_index = 2

            #formatted_str = f"{number:06.2f}"
            result_string += f"""{data_end[player]:06.2f} | {up_down_neutral_emoji[compare_index]} {compare_difference:04.2f} | {player}\n"""
        
        return  result_string

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
    pass


if __name__ == "__main__":
    main()