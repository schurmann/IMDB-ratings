from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists

from models import Base, engine, User
from spiders.ratings_spider import RatingsSpider

if database_exists(engine.url):
    Base.metadata.bind = engine
    Base.metadata.drop_all()
Base.metadata.create_all(engine)
session = Session(bind=engine)
users = [User(id=k, name=v) for k, v in RatingsSpider.users.items()]
session.add_all(users)
session.commit()
