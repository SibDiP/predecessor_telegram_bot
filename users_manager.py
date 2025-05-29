import logging
import traceback

from sqlalchemy import (
    create_engine, Column, BigInteger, Integer, Float, String, Index,
    select, delete, update, bindparam
    )
from sqlalchemy.orm import sessionmaker, declarative_base
from threading import Lock

import ps_parser

logger = logging.getLogger(__name__)

Base = declarative_base()

# Модель для создания таблицы пользователей
class UsersModel(Base):
    NAME_LEN = 25
    OMEDA_ID_LEN = 40
    
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    name = Column(String(NAME_LEN), nullable=False)
    omeda_id = Column(String(OMEDA_ID_LEN), nullable=False)
    player_ps_day = Column(Float, nullable=False)
    __table_args__ = (
        Index('idx_chat_id_name', 'chat_id', 'name'),
    )



# Контроллер для CRD пользователей в БД
class UsersController:
    _instance = None
    _lock = Lock()

    def __new__(cls):

        """
        Проверка на существование объекта класса и создание синглтона
        """
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Создание базы данных и sessionmaker
        """
        if not hasattr(self,'_initialized'):
            self._initialized = True
    
            self.engine = create_engine('sqlite:///ps_data.db')
            Base.metadata.create_all(self.engine)
            logger.info("Users base creation: Success")

            self.Session = sessionmaker(bind=self.engine)

    async def add_player(self,
        name: str, 
        omeda_id: str, 
        chat_id: int) -> None: 
        """
        Добавляет нового игрока в базу данных. +парсит его PS
        
        Args:
            name (str): Никнейм игрока (макс. 25 символов)
            omeda_id (str): Omeda ID игрока (макс. 40 символов)
            chat_id (int): ID чата, к которому привязан игрок
            
        Returns:
            Users: Созданный объект пользователя
            
        Raises:
            ValueError: Если данные не соответствуют ограничениям
            sqlalchemy.exc.SQLAlchemyError: При ошибках БД
        """
        player_ps = await ps_parser.get_player_ps_from_api(omeda_id)

        # Валидация
        if len(name) > UsersModel.NAME_LEN:
            raise ValueError(f"Имя должно быть не более {UsersModel.NAME_LEN} символов")
        if len(omeda_id) > UsersModel.OMEDA_ID_LEN:
            raise ValueError(f"Omeda_id должен быть не более {UsersModel.OMEDA_ID_LEN} символов")
        
       
       
        session = self.Session()
        try:
            new_user = UsersModel(
                name=name,
                omeda_id=omeda_id,
                chat_id=chat_id,
                player_ps_day=player_ps,
            )

            session.add(new_user)
            session.commit()

            return new_user

        except Exception as e:
            logger.info("Добавить пользователя не удалось")
            session.rollback()
            raise e
        finally:
            session.close()
    
    def del_player_from_db(self, player_name: str, chat_id: int) -> None:
        """
        Удаляет игрока из базы данных.
        """
        with self.Session() as session:
            try:
                stmt = delete(UsersModel).where(
                    UsersModel.name == player_name, 
                    UsersModel.chat_id == chat_id
                    )
                session.execute(stmt)
                session.commit()

            except Exception as e:
                logger.error("Удалить пользователя не удалось")
                logger.error(e)
                logger.error(traceback.format_exc())
                session.rollback()
                raise e

    def get_users_and_omeda_id(self, chat_id: int = 0
    ) -> dict[str, dict[str, str| int]]:
        """
        Возвращает словарь пользователей указанного чата, либо для всех
        пользователей если чат не указан

        Args:
            chat_id (int): Идентификатор чата.

        Returns:
            dict[str, dict[str, str| int]]: Словарь, где ключом является имя 
            пользователя, а значением — словарь с 
            bd_id(в БД)
            Omeda ID пользователя
            player_ps_day

        Raises:
            Exception: Если не удалось получить данные пользователей из БД.
        """
        
        with self.Session() as session:
            try:
                stmt = select(
                    UsersModel.name, 
                    UsersModel.omeda_id, 
                    UsersModel.id,
                    UsersModel.player_ps_day
                )
                if chat_id != 0:
                    stmt = stmt.where(UsersModel.chat_id == chat_id)
            
                users = session.execute(stmt)

                team_dict = {
                    user.name: {
                        'bd_id': user.id, 
                        'omeda_id': user.omeda_id, 
                        'player_ps_day': user.player_ps_day
                        } for user in users}
                logger.debug(f"Team dict: {team_dict}")
                logger.info(f"chat_id: {chat_id}. Получили данные пользователей из БД")
                return team_dict

            except Exception as e:
                logger.error("Не удалось получть данные пользователей из БД")
                raise e

   
    async def update_player_ps_day(self, users_dict: 
        dict[str, dict[str, int | float]]):
        """
        Заменяем значения столбца player_ps_day в БД ps_data.db
        Вид принимаемого аргумента - name : {'bd_id':int, 'player_ps': float}
        """
        #TODO вынести в отдельную функцию
        users_to_update = [
            {
                'id': user_data['bd_id'],
                'player_ps_day': user_data['player_ps_day']
            }
            for user_data in users_dict.values()
        ]
        logger.debug(f"users_to_update: {users_to_update}")

        with self.Session() as session:
            try:
                stmt = (
                    update(UsersModel)
                    .where(UsersModel.id == bindparam('id'))
                    .values(player_ps_day=bindparam('player_ps_day'))
                )

                session.execute(stmt, users_to_update)
                session.commit()
            
            except Exception as e:
                session.rollback()
                logger.error(f"Обновление player_ps_day не удалось. Exception: {e}")
        
        return
               
class Player:
    def __init__(self, name, omeda_id):
        self.name = name
        self.omeda_id













# Legacy

# Traced players. {nik_name : id}
PLAYERS_ADRESSES = {
    "evvec" : "d6f5c363-6550-4af2-a84e-2d8e68e0010b",
    "good boy 69 69" : "eaacae21-0d28-4611-beb4-815bbc191d38",
    "PowerSobaka9000" : "d721a45e-c57a-4b8e-b866-8179d1365dfa",
    "sibdip" : "22721c84-9d9e-4bdc-a6d6-758806afa0b1",
    "styxara" : "304a359b-2329-4ea7-8007-095e292f382e",
    }