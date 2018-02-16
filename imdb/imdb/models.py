from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Boolean, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine('mysql+mysqldb://root:root@localhost:3306/imdb', echo=True)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(String(10), primary_key=True)
    name = Column(String(50))
    ratings = relationship('Rating', back_populates='user')


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(String(9), primary_key=True)
    imdb_score = Column(Numeric)
    title = Column(String(500))
    director = Column(String(500))
    year = Column(Integer)
    is_movie = Column(Boolean)
    ratings = relationship('Rating', back_populates='movie')
    added = Column(DateTime)


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_score = Column(Integer)
    movie_id = Column(String(9), ForeignKey('movies.id'))
    movie = relationship('Movie', back_populates='ratings')
    user_id = Column(String(10), ForeignKey('users.id'))
    user = relationship('User', back_populates='ratings')
    added = Column(DateTime)
    updated = Column(DateTime)
