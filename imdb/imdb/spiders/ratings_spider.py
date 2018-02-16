import scrapy
import re
from dateutil.parser import parse


class RatingsSpider(scrapy.Spider):
    name = "ratings"
    users = {
        'ur45228865': 'Joppe',
        'ur31082080': 'Isak',
        'ur30235107': 'Simon',
        'ur38393176': 'Albin',
        'ur38638840': 'Elon'
    }
    selectors_css = {
        'title': 'b a::text',
        'user_score': 'span.rating-rating.rating-your span.value::text',
        'imdb_score': 'div.rating::attr(id)',
        'director': 'div.secondary a::text',
        'year': 'b span::text',
        'is_movie': 'b span::text'
    }

    selectors_xpath = {
        'title': 'div[2]/h3/a/text()',
        'imdb_id': 'div[2]/h3/a/@href',
        'user_score': 'div[2]/div[2]/div[2]/span[2]/text()',
        'imdb_score': 'div[2]/div[2]/div[1]/span[2]/text()',
        'rated': 'div[2]/p[2]/text()',
        'director': 'div[2]/p[4]/a[1]/text()',
        'year': 'div[2]/h3/span[3]/text()'
    }

    def start_requests(self):
        urls = [f'http://www.imdb.com/user/{user}/ratings' for user in self.users.keys()]
        for index, url in enumerate(urls):
            request = scrapy.Request(url=url, callback=self.parse, meta={'user': list(self.users)[index]})
            yield request

    def parse(self, response):
        for movie in response.css('div.lister-item'):
            if len(movie.xpath(self.selectors_xpath['title'])) == 2:  # Series episode
                continue
            year = movie.xpath(self.selectors_xpath['year']).extract_first()
            is_movie = None
            if year is None:
                year = ""
            else:
                is_movie = not '–' in year  # NOT dash char (-)
                year = re.search(r'\d{4}', year).group()
            yield {
                'user': response.meta['user'],
                'title': movie.xpath(self.selectors_xpath['title']).extract_first(),
                'imdb_id': movie.xpath(self.selectors_xpath['imdb_id']).extract_first()[7:16],
                'user_score': int(movie.xpath(self.selectors_xpath['user_score']).extract_first()),
                'imdb_score': float(movie.xpath(self.selectors_xpath['imdb_score']).extract_first()),
                'rated': parse(movie.xpath(self.selectors_xpath['rated']).extract_first()[9:]),
                'year': year,
                'is_movie': is_movie,
                'director': '' if not is_movie else movie.xpath(self.selectors_xpath['director']).extract_first(),
            }
            next_page = response.css('a.next-page::attr(href)').extract_first()
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse, meta={'user': response.meta['user']})
