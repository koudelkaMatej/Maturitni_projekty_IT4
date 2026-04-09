from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, mapped_column
import datetime
from typing import TypedDict, Optional, Any, Type
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import OperationalError
import os

DATABASE_FILE = 'ditr.db'
DATABASE_URL = f'sqlite:///instance/{DATABASE_FILE}'

if not os.path.exists("instance"):
    os.makedirs("instance")

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(TypedDict):
    id: int
    username: str
    password_hash: str
    email: str
    created_at: datetime.datetime
    prefered_scheme: Optional[str]
    role: Optional[str]
    banned: bool
    
    game_sessions: Optional[list['GameSession']]

class GameSession(TypedDict):
    id: int
    user_id: int
    started_at: datetime.datetime
    score: int
    level_reached: int
    invalid: bool
    user: Optional['User']








class UserModel(Base, UserMixin):
    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String, unique=True, nullable=False)
    password_hash = mapped_column(String, nullable=False)
    email = mapped_column(String, unique=True, nullable=False)
    created_at = mapped_column(DateTime, default=datetime.datetime.now())
    game_sessions = relationship('GameSessionModel', back_populates='user')
    prefered_scheme = mapped_column(String, nullable=True)
    role = mapped_column(String, nullable=True, default="user", server_default="user")
    banned = mapped_column(Integer, nullable=False, default=0, server_default="0")

    def set_password(self, password:str):
        """Sets/Resets the password

        Args:
            password (str): Password string
        """
        self.password_hash = generate_password_hash(password)
        if getattr(self, 'id', None) is not None:
            session = Session()
            try:
                session.query(UserModel).filter_by(id=self.id).update({'password_hash': self.password_hash})
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

    def check_password(self, password:str):
        """Checks the entered password with the hashed password stored in DB

        Args:
            password (str): the entered password

        Returns:
            bool: returns True if entered password is correct and user should be logged in, otherwise False
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', created_at='{self.created_at}')>"
    
    

class GameSessionModel(Base):
    __tablename__ = 'game_sessions'

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    started_at = mapped_column(DateTime, default=datetime.datetime.now())
    score = mapped_column(Integer, default=0)
    level_reached = mapped_column(Integer, default=1)
    invalid = mapped_column(Integer, nullable=False, default=0, server_default="0")

    user = relationship('UserModel', back_populates='game_sessions')

    def __repr__(self):
        return f"<GameSession(id={self.id}, user_id={self.user_id}, started_at='{self.started_at}', score={self.score}, level_reached={self.level_reached}), invalid={self.invalid}>"




Base.metadata.create_all(bind=Session().get_bind())

with Session() as session:
    try:
        admin_user = session.query(UserModel).filter_by(username="admin").first()
        anonymous_user = session.query(UserModel).filter_by(username="Anonymous").first()

        if admin_user is None:
            admin = UserModel(
                username="admin",
                email="admin@admin.com",
                password_hash=generate_password_hash("admin"),
                role="admin",
                banned=0,
            )
            session.add(admin)

        if anonymous_user is None:
            anon = UserModel(
                username="Anonymous",
                email="",
                password_hash=generate_password_hash(""),
                role="user",
                banned=0,
            )
            session.add(anon)

        if admin_user is None or anonymous_user is None:
            session.commit()
    except Exception as e:
        session.rollback()
        print(e)