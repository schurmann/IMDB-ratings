import logging

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
import google_sheets

if __name__ == '__main__':
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='/tmp/scraper.log',
        format='%(created) - f%(levelname)s: %(message)s',
        level=logging.INFO
    )
    process = CrawlerProcess(get_project_settings())
    process.crawl('ratings')
    process.start()
    google_sheets.upload()
