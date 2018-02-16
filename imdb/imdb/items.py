# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Rating(scrapy.Item):
    user = scrapy.Field()
    title = scrapy.Field()
    my_score = scrapy.Field()
    imdb_score = scrapy.Field()
    director = scrapy.Field()
    year = scrapy.Field()
    is_movie = scrapy.Field()
