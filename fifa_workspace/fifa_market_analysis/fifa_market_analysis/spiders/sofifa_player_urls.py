import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from fifa_market_analysis.items import MainPageItem
from fifa_market_analysis.proxy_generator import proxies
from fifa_market_analysis.user_agent_generator import user_agent
from fifa_market_analysis.sofifa_settings import sofifa_settings
from fifa_market_analysis.custom_logging import *
from fifa_market_analysis.custom_stats import *


class SofifaPlayerURLsSpider(CrawlSpider):

    name = 'player_pages'

    allowed_domains = ['sofifa.com']
    start_urls = ['https://sofifa.com/players/']

    rules = (
        Rule(LinkExtractor(deny=([r'\?', r'[0-9]+/[0-9]+/', r'/changeLog', r'/live', r'/squads', r'/calculator/',
                                  r'/team/', r'[0-9]+', r'/[a-zA-Z0-9]+$'])),
             callback='parse_item', follow=True),
        Rule(LinkExtractor(restrict_xpaths="//a[text()='Next']"), callback='parse_item', follow=True)
    )

    custom_settings = sofifa_settings(name=name, proxies=proxies, user_agent=user_agent, collection='player_urls',
                                      validator='PlayerItem')

    def parse_item(self, response):

        """
        @url http://sofifa.com/players/
        @returns items 1 61
        @returns requests 0 0
        @scrapes id_player_main total_stats hits comments player_page
        """

        self.crawler.stats.set_value('page_counter', page_counter(response.url))

        for row in response.xpath("//table[@class='table table-hover persist-area']/tbody/tr"):
            loader = ItemLoader(item=MainPageItem(), selector=row, response=response)

            loader.add_xpath('id', ".//a[contains(@href, 'player/')]/@href")
            loader.add_xpath('total_stats', ".//div[@class='col-digit col-tt']/text()")
            loader.add_xpath('hits', ".//div[@class='col-comments text-right text-ellipsis rtl']/text()")
            loader.add_xpath('comments', ".//div[@class='col-comments text-right text-ellipsis rtl']/text()")
            loader.add_xpath('player_page', ".//a[contains(@href, 'player/')]/@href")

            print(response.request.headers['User-Agent'])

            self.logger.info(f'Currently on page {current_page(response.url)}')

            yield loader.load_item()
