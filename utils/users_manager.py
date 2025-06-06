"""
Управляет пользовательскими данными в базе SQLite с использованием SQLAlchemy ORM.

Этот класс реализует шаблон Singleton для операций с базой данных, связанных с пользователями,
и предоставляет методы для добавления, удаления, получения и обновления информации о пользователях.

Ключевые особенности:
    Потокобезопасная реализация Singleton
    Операции создания, чтения и удаления записей пользователей
    Поддержка хранения данных пользователя: имя, Omeda ID, ID чата и показатели эффективности
    Логирование и обработка ошибок при работе с базой данных

Атрибуты:
_instance (UsersController): Единственный экземпляр класса (Singleton)
_lock (threading.Lock): Блокировка для синхронизации потоков при создании Singleton
"""
import logging
import traceback

from sqlalchemy import (
    create_engine, Column, BigInteger, Integer, Float, String, Index,
    select, delete, update, bindparam
    )
from sqlalchemy.orm import sessionmaker, declarative_base
from threading import Lock
from sqlalchemy.orm.exc import NoResultFound


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
    """
    Класс для работы с пользователями в БД.
    """
    #Тут храним единственный инстанс класса
    _instance = None
    #Блокировка для создания синглтона
    _lock = Lock()
    
    def __new__(cls):
        """
        Проверка на существование объекта класса и создание синглтона
        """
        #болокируем доступп к созданию объекта, чтобы не было одновременного 
        #создания нескольких объектов
        with cls._lock:
            #если объект еще не создан, то создаем его
            if not cls._instance:
                #создаем объект класса через базовый класс object, 
                #что б не словить рекурсию
                cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        """
        Создание базы данных и sessionmaker
        """

        self.engine = create_engine('sqlite:///ps_data.db')
        Base.metadata.create_all(self.engine)
        logger.info("Users base creation: Success")
        self.Session = sessionmaker(bind=self.engine)

    async def add_player(self,
        name: str, 
        omeda_id: str, 
        chat_id: int,
        player_ps: float) -> None: 
        """
        Добавляет нового игрока в базу данных. +парсит его PS
        
        Args:
            name (str): Никнейм игрока (макс. 25 символов)
            omeda_id (str): Omeda ID игрока (макс. 40 символов)
            chat_id (int): ID чата, к которому привязан игрок
            player_ps (float): PS игрока
            
        Returns:
            Users: Созданный объект пользователя
            
        Raises:
            ValueError: Если данные не соответствуют ограничениям
            Exeption: При прочих ошибках при добавлении в БД
            
            aiohttp.ClientError при ошибках соединения (fetch_api_data)
            aiohttp.ClientResponseError ответ сервера отличен от 200 (fetch_api_data)
            aiohttp.TimeoutError при превышении таймаута (fetch_api_data)
        """

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
            logger.error(f"Добавить пользователя в базу данных не удалось: {e}")
            session.rollback()
            raise

        finally:
            session.close()
    
    def del_player_from_db(self, 
        player_name: str, 
        chat_id: int) -> None:
        """
        Удаляет игрока из базы данных.

        Args:
            player_name (str): Имя игрока
            chat_id (int): ID чата, к которому привязан игрок
        Returns:
            None:
        Raises:
            ValueError: Если данные не соответствуют ограничениям
            Exeption: При прочих ошибках при удалении из БД
        """
        with self.Session() as session:
            try:
                stmt = delete(UsersModel).where(
                    UsersModel.name == player_name, 
                    UsersModel.chat_id == chat_id
                    )
                result = session.execute(stmt)
                session.commit()           

            except Exception as e:
                logger.error(f"Удалить пользователя не удалось: {e}")
                logger.error(traceback.format_exc())
                session.rollback()
                raise

            if result.rowcount == 0:
                logger.error("Пользователь не найден")
                raise NoResultFound("Пользователь не найден")

    def get_users_and_omeda_id(self, chat_id: int = 0
    ) -> dict[str, dict[str, str| int]]:
        """
        Возвращает словарь пользователей указанного чата, либо для всех
        пользователей если чат не указан

        Args:
            chat_id (int): Идентификатор чата.

        Returns:
            dict[str, dict[str, str| int]]: Словарь, где ключом является имя 
            пользователя, а значением — словарь со следующими ключами:
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
                logger.error(f"Не удалось получть данные пользователей из БД: {e}")
                logger.error(traceback.format_exc())
                raise

    def _make_users_to_update_list(self,
    users_dict: dict[str, dict[str, int | float]]
    ) -> list[dict[str, int | float]]:
        """
        Создает словарь для обновления данных в БД

        Args:
            users_dict (dict[str, dict[str, int | float]]): Словарь пользователей

        Returns:
            list[dict[str, int | float]]: Список словарей для обновления данных в БД
        """
        users_to_update = [
            {
                'id': user_data['bd_id'],
                'player_ps_day': user_data['player_ps_day']
            }
            for user_data in users_dict.values()
        ]

        logger.debug(f"users_to_update: {users_to_update}")

        return users_to_update

    async def update_player_ps_day(self, 
    users_dict: dict[str, dict[str, int | float]]):
        """
        Заменяем значения столбца player_ps_day в БД ps_data.db
        Вид принимаемого аргумента - name : {'bd_id':int, 'player_ps': float}
        """
        users_to_update = self._make_users_to_update_list(users_dict)

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
                raise
        
        return None

def __main__():
    pass


if __name__ == "__main__":
    __main__()