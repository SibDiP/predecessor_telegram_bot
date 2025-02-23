import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_ps_to_pd_dataframe(players_score : dict[str, float]) -> pd.DataFrame:
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

    logger.debug(f"\n{df.to_string()}")
    logger.info("Create pandas DataFrame: Success")

    return df

def write_df_to_csv(dataframe : pd.DataFrame, csv_name:str="by_weeks") -> None:
    """
    Write pd.DataFrame object to a .csv file.

    ::parameters::
    dataframe : pd.DataFrame
        The DataFrame to export.
    csv_name : str
        Name of the .csv file to export. Default is "by_weeks.csv".
    """
    dataframe.to_csv(csv_name, index=False)
    logger.info(f"Saving data in {csv_name}.csv: Success")

def read_df_from_csv(csv_name) -> pd.DataFrame:
    """
    Read pd.DataFrame object from .csv file
    """
    pass
