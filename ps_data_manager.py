import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

def ps_data_save(players_score : dict[str, float]) -> None:
    print(players_score)
    df = pd.DataFrame(data=players_score, index=[0]).T
    print(df)
