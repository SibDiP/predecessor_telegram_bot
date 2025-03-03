import os
import pandas as pd
import logging
import sqlite3
import sqlalchemy

from datetime import datetime
import players

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PLAYERS_FOR_SQL = [k.replace(' ','_') for k in players.PLAYERS_ADRESSES.keys()]


def convert_ps_to_pd_dataframe(players_score : dict[str, float]) -> pd.DataFrame:
    """
    Convert Player Score dictionary to pandas DataFrame with three
    columns: id, Player, Player Score

    return: pd.DataFrame
    """

    df = pd.DataFrame(data=players_score, index=[0])
    df['date'] = datetime.now().strftime('%Y-%m-%d')
    df = df.set_index('date')

    logger.debug(f"\n{df.to_string()}")
    logger.info("Create pandas DataFrame: Success")

    return df

def create_sql_database(sql_database : "str" = "ps_data.db") -> None:
    """
    Write pd.DataFrame object to .sqliete 
    """
    if os.path.isfile(sql_database):
        logger.info(f"SQLite database creating: {sql_database} already exist")
    else:
        connection = sqlite3.connect(sql_database)
        coursor = connection.cursor()
        
        # Create table
        coursor.execute(f'''
        CREATE TABLE IF NOT EXISTS players_Score (
        date TEXT PRIMARY KEY,
        {", ".join([f"{player} REAL NOT NULL" 
        for player in PLAYERS_FOR_SQL])}
        )
        ''')
        
        logger.info(f"SQLite database {sql_database} creating: Success")

        # Save table
        connection.commit()
        connection.close()

    return None


def write_df_to_sql_database(dataframe : pd.DataFrame, 
sql_database : "str"="ps_data.db",
sql_database_table : "str"="players_score") -> None:
    
    if dataframe.empty:
        logger.warning("DataFrame is empty. No data written to the database.")
    else:
        engine = sqlalchemy.create_engine(f'sqlite:///{sql_database}', echo=False)
        try:
            dataframe.to_sql(
                sql_database_table, 
                con=engine, 
                index_label="date",
                if_exists='append',)

            logger.info(f"DataFrame writting to {sql_database}: Succsess")
        except sqlalchemy.exc.IntegrityError:
            logger.debug(f"write_df_to_sql_database: This date row already exist in {sql_database}")

    return None
