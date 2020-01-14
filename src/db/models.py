from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(String(10), primary_key=True, nullable=False)
    name = Column(String(50), nullable=False)
    ratings = relationship('Rating', back_populates='user', cascade='all, delete-orphan')


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    director = Column(String(500), nullable=False)
    year = Column(Integer, nullable=False)
    entry_id = Column(String(9), ForeignKey('entries.id'), nullable=False)
    entry = relationship('Entry', back_populates='movie')


class Show(Base):
    __tablename__ = 'shows'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_year = Column(String(4), nullable=False)
    end_year = Column(String(4), nullable=True)
    entry_id = Column(String(9), ForeignKey('entries.id'), nullable=False)
    entry = relationship('Entry', back_populates='show')


class Entry(Base):
    __tablename__ = 'entries'

    id = Column(String(9), primary_key=True, nullable=False)
    imdb_score = Column(String(3), nullable=False)
    title = Column(String(500), nullable=False)
    added = Column(DateTime)
    votes = Column(Integer, nullable=False)
    ratings = relationship('Rating', back_populates='entry')
    movie = relationship('Movie', order_by=Movie.id, uselist=False, back_populates='entry',
                         cascade='all, delete-orphan')
    show = relationship('Show', order_by=Show.id, uselist=False, back_populates='entry', cascade='all, delete-orphan')


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_score = Column(Integer)
    entry_id = Column(String(9), ForeignKey('entries.id'))
    entry = relationship('Entry', back_populates='ratings')
    user_id = Column(String(10), ForeignKey('users.id'))
    user = relationship('User', back_populates='ratings')
    added = Column(DateTime)
