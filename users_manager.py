import logging
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, Column, BigInteger, Integer, String, Index
from sqlalchemy.orm import sessionmaker
from threading import Lock

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



# Контроллер для CRD пользователей в БД
class UsersСontroller:
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
            logger.info(f"Users base creation: Success")

            self.Session = sessionmaker(bind=self.engine)

    def add_player(self,
        name: str, 
        omeda_id: str, 
        chat_id: str):
        """
        Добавляет нового игрока в базу данных
        
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
                chat_id=chat_id
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
    
    def get_chat_users_and_omeda_id(self, chat_id: int):
        """
        Возвращает словарь пользователей указанного чата.

        Args:
            chat_id (int): Идентификатор чата.

        Returns:
            dict[str, dict[str, str]]: Словарь, где ключом является имя 
            пользователя, а значением — словарь с Omeda ID пользователя.

        Raises:
            Exception: Если не удалось получить данные пользователей из БД.
        """
        
        with self.Session() as session:
            try:
                users = session.query(UsersModel).filter_by(chat_id=chat_id).all()
                team_dict = {user.name: {'omeda_id': user.omeda_id} for user in users}
                logger.debug(f"Team dict: {team_dict}")
                return team_dict
            except Exception as e:
                logger.info("Не удалось получть данные пользователей из БД")
                raise e













    @staticmethod
    def remove_player(name):
        pass


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