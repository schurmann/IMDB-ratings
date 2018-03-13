from requests_html import HTMLSession
import re

url = 'http://www.imdb.com/user/ur45228865/ratings?sort=date_added,asc'


class TestXPath(object):
    def test_one(self):
        print('test_one')
        session = HTMLSession()
        r = session.get(url)
        rating = r.html.find('div.lister-item', first=True)
        title = rating.xpath('//div[2]/h3/a/text()', first=True)
        assert title == 'Argo'
        imdb_id = rating.xpath('//div[2]/h3/a/@href', first=True)[7:16]
        assert imdb_id == 'tt1024648'
        user_score = rating.xpath('//div[2]/div[2]/div[2]/span[2]/text()', first=True)
        assert user_score.isdigit()
        imdb_score = rating.xpath('//div[2]/div[2]/div[1]/span[2]/text()', first=True)
        match = re.search(r'\d\.\d', imdb_score)
        assert match
        rated_date = rating.xpath('//div[2]/p[2]/text()', first=True)
        assert rated_date == 'Rated on 20 Jul 2013'
        director = rating.xpath('//div[2]/p[4]/a[1]/text()', first=True)
        assert director == 'Ben Affleck'
        year = rating.xpath('//div[2]/h3/span[3]/text()', first=True)[1:-1]
        assert year == '2012'
        votes = rating.xpath('//div[2]/p[5]/span[2]/text()', first=True).replace(',', '')
        match = re.search(r'\d{6,}', votes)
        assert match
