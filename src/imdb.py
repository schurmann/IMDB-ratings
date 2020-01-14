import logging
from os import path

from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from db import Database
from definitions import USERS


def init_db():
    if not path.exists('../db.sqlite'):
        db = Database()
        db.create_tables(USERS)


if __name__ == '__main__':
    init_db()
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='/tmp/scraper.log',
        format='%(created) - f%(levelname)s: %(message)s',
        level=logging.INFO
    )
    process = CrawlerProcess(get_project_settings())
    process.crawl('ratings')
    process.start()
    import google_sheets

    google_sheets.upload()
