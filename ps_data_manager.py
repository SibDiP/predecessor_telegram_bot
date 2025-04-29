import os
import pandas as pd
import logging
import sqlite3

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

from datetime import datetime
import players


#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# SQLAlchemy
Base = declarative_base()

#PLAYERS_FOR_SQL = [k.replace(' ','_') for k in players.PLAYERS_ADRESSES.keys()]

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    name = Column(String(25))
    omeda_id = Column(String(40))

def create_sql_players_database() -> None:
    engine = create_engine('sqlite:///ps_data.db')
    Base.metadata.create_all(engine)


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

        # Save table
        connection.commit()
        logger.info(f"SQLite database {sql_database} creating: Success")
        connection.close()

    return None


def write_df_to_sql_database(dataframe : pd.DataFrame, 
sql_database : "str"="ps_data.db",
sql_database_table : "str"="players_score") -> None:
    
    if dataframe.empty:
        logger.warning("DataFrame is empty. No data written to the database.")
    else:
        engine = create_engine(f'sqlite:///{sql_database}', echo=False)
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


if __name__ == '__main__':
    create_sql_players_database()