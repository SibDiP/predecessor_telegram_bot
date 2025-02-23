import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def ps_to_pd_dataframe(players_score : dict[str, float]) -> pd.DataFrame:
    """
    Convert Player Score dictionary to pandas DataFrame with three
    columns: id, Player, Player Score

    return: pd.DataFrame
    """
    df = pd.DataFrame(data=list(players_score.items()), columns=
    [
        "Player",
        "Player Score"],
        )

    logger.debug("\n%s", df.to_string())
    logger.info("Create pandas DataFrame: Success")

    return df

