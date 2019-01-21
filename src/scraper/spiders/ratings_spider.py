import scrapy
import re
from dateutil.parser import parse

from db import DB


class RatingsSpider(scrapy.Spider):
    name = "ratings"
    selectors_xpath = {
        'title': 'div[2]/h3/a/text()',
        'imdb_id': 'div[2]/h3/a/@href',
        'user_score': 'div[2]/div[2]/div[2]/span[2]/text()',
        'imdb_score': 'div[2]/div[2]/div[1]/span[2]/text()',
        'rated_date': 'div[2]/p[2]/text()',
        'director': 'div[2]/p[4]/a[1]/text()',
        'year': 'div[2]/h3/span[3]/text()',
        'votes': 'div[2]/p[5]/span[2]/text()'
    }

    def start_requests(self):
        users = DB.users()
        urls = [f'http://www.imdb.com/user/{user.id}/ratings' for user in users]
        for index, url in enumerate(urls):
            request = scrapy.Request(url=url, callback=self.parse, meta={'user': list(users)[index]})
            yield request

    def parse(self, response):
        for entry in response.css('div.lister-item'):
            if len(entry.xpath(self.selectors_xpath['title'])) == 2:  # Series episode
                continue
            year = entry.xpath(self.selectors_xpath['year']).extract_first()
            is_movie = not year or '–' not in year
            data = self.parse_movie(entry) if is_movie else self.parse_show(entry)
            data['user_id'] = response.meta['user']
            data.update(self.parse_common(entry))
            yield data
            next_page = response.css('a.next-page::attr(href)').extract_first()
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse, meta={'user': response.meta['user']})

    def parse_movie(self, entry) -> dict:
        return {
            'year': re.search(r'\d{4}', entry.xpath(self.selectors_xpath['year']).extract_first()).group(0),
            'director': entry.xpath(self.selectors_xpath['director']).extract_first(),
            'is_movie': True
        }

    def parse_show(self, entry) -> dict:
        years = re.findall(r'\d{4}', entry.xpath(self.selectors_xpath['year']).extract_first())
        return {
            'start_year': years[0],
            'end_year': years[1] if len(years) == 2 else None,
            'is_movie': False
        }

    def parse_common(self, entry) -> dict:
        return {
            'imdb_id': entry.xpath(self.selectors_xpath['imdb_id']).extract_first()[7:16],
            'imdb_score': float(entry.xpath(self.selectors_xpath['imdb_score']).extract_first()),
            'title': entry.xpath(self.selectors_xpath['title']).extract_first(),
            'user_score': int(entry.xpath(self.selectors_xpath['user_score']).extract_first()),
            'rated_date': parse(entry.xpath(self.selectors_xpath['rated_date']).extract_first()[9:]),
            'votes': entry.xpath(self.selectors_xpath['votes']).extract_first().replace(',', '')
        }
