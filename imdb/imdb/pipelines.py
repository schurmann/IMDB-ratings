# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime
from scrapy import Spider
from scrapy.crawler import Crawler
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import Session

from .models import User, Movie, Rating


class ImdbPipeline:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.session = Session(bind=self.engine, autoflush=False)
        self.users = {u.id: u for u in self.session.query(User).all()}

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(crawler.settings.get('DB_URI'))

    def open_spider(self, spider: Spider):
        pass

    def close_spider(self, spider: Spider):
        self.session.close()

    def process_item(self, item: dict, spider: Spider):
        movie = self.session.query(Movie).filter(Movie.id == item['imdb_id']).first()
        if movie is None:
            movie = Movie(id=item['imdb_id'],
                          title=item['title'],
                          imdb_score=item['imdb_score'],
                          director=item['director'],
                          year=item['year'],
                          is_movie=item['is_movie'])
            self.session.add(movie)
        rating = self.session.query(Rating).filter(and_(Rating.user_id == item['user'], Rating.movie == movie)).first()
        if rating is None:
            rating = Rating(user_score=item['user_score'], added=datetime.now(), updated=datetime.now())
            print(f'New rating: {movie.title} - {rating.user_score}')
            self.users[item['user']].ratings.append(rating)
            movie.ratings.append(rating)
        elif rating.user_score != item['user_score']:
            print(f'''Rating updated: {movie.title} - {rating.user_score}->{item['user_score']}''')
            rating.user_score = item['user_score']
            rating.updated = datetime.now()
        self.session.commit()
        self.session.flush()
        return item
