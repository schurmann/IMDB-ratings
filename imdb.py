from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import google_sheets

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl('ratings')
    process.start()
    google_sheets.upload()
