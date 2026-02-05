from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, mapped_column
import datetime
from typing import TypedDict, Optional, Any, Type
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload

DATABASE_FILE = 'gradproj.db'
DATABASE_URL = f'sqlite:///instance/{DATABASE_FILE}'

engine = create_engine(DATABASE_URL)
Base = declarative_base()



def session_init():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


class User(TypedDict):
    id: int
    username: str
    email: str
    created_at: datetime.datetime

    game_sessions: Optional[list['GameSession']]

class UserAccess(TypedDict):
    id: int
    user_id: int
    password_hash: str
    last_login: Optional[datetime.datetime]
    reset_mail: Optional[str]

class GameSession(TypedDict):
    id: int
    user_id: int
    started_at: datetime.datetime
    score: int
    level_reached: int
    user: Optional['User']








class UserModel(Base, UserMixin):
    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String, unique=True, nullable=False)
    password_hash = mapped_column(String, nullable=False)
    email = mapped_column(String, unique=True, nullable=False)
    created_at = mapped_column(DateTime, default=datetime.datetime.now())
    game_sessions = relationship('GameSessionModel', back_populates='user')

    def set_password(self, password, persist: bool = True):
        self.password_hash = generate_password_hash(password)
        if persist and getattr(self, 'id', None) is not None:
            session = session_init()
            try:
                session.query(UserModel).filter_by(id=self.id).update({'password_hash': self.password_hash})
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

    def check_password(self, password):
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

    user = relationship('UserModel', back_populates='game_sessions')


Base.metadata.create_all(bind=session_init().get_bind())

def insert_row(model: Type[Any], data: dict[str, Any]) -> Any:
    session = session_init()
    try:
        new_record = model(**data)
        session.add(new_record)
        session.commit()
        session.refresh(new_record)
        return new_record
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def query_rows(model: Type[Any], filters: Optional[dict[str, Any]] = None, include: Optional[list[str]] = None) -> list[Any]:
    """
    Query rows for `model`. If `include` is provided (list of relationship attribute names),
    the related objects will be eagerly loaded and returned as nested dicts alongside the
    model's column data. If `include` is None, SQLAlchemy model instances are returned.
    """
    session = session_init()
    try:

        query = session.query(model)

        # Eager-load requested relationships
        if include:
            for rel in include:
                query = query.options(joinedload(getattr(model, rel)))

        # Apply filters
        if filters:
            for attr, value in filters.items():
                query = query.filter(getattr(model, attr) == value)

        results = query.all()

        # If no relationships requested, return the raw ORM objects
        if not include:
            return results

        # Helper to convert an ORM instance to dict (columns + requested relationships)
        def instance_to_dict(obj):
            data = {}
            # columns
            for col in obj.__table__.columns:
                data[col.name] = getattr(obj, col.name)
            # relationships
            for rel in include:
                if not hasattr(obj, rel):
                    continue
                val = getattr(obj, rel)
                if val is None:
                    data[rel] = None
                else:
                    # detect collection-like relationship (InstrumentedList etc.)
                    if hasattr(val, '__iter__') and not hasattr(val, '__table__'):
                        data[rel] = []
                        for item in val:
                            # for related items, include only their columns (no further nesting)
                            sub = {}
                            for c in item.__table__.columns:
                                sub[c.name] = getattr(item, c.name)
                            data[rel].append(sub)
                    else:
                        # single related object
                        sub = {}
                        for c in val.__table__.columns:
                            sub[c.name] = getattr(val, c.name)
                        data[rel] = sub
            return data

        return [instance_to_dict(r) for r in results]
    finally:
        session.close()
