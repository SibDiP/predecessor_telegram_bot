import pytest
from utils.ps_analitic_tools import Analitic


def test_difference_players_score_records_success(sample_player_data):

    result = Analitic.difference_players_score_records(
        sample_player_data['start_data'], 
        sample_player_data['end_data']
        )
    
    assert "player1" in result # nick
    assert "100.00" in result # avg
    assert "110.70" in result # last
    assert "1.00" in result # delta