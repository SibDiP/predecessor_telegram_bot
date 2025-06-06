import pytest


@pytest.fixture
def sample_player_data():
    return {
        'start_data': {
            'player1': {'player_ps_day': 100.00},
        },
        'end_data': {
            'player1': {'player_ps_day': 101.00,
            'last_match_ps': 110.7,
            'omeda_id': '304a359b-2329-4ea7-8007-095e292f382e',}
        }
    }
