import scrapy
from scrapy.loader import ItemLoader
from fifa_market_analysis.items import SofifaItem
from pymongo import MongoClient
from fifa_market_analysis.proxy_generator import proxies
from fifa_market_analysis.user_agent_generator import user_agent
from fifa_market_analysis.sofifa_settings import sofifa_settings
from fifa_market_analysis.custom_logging import *
from fifa_market_analysis.custom_stats import *


class SofifaPlayerPagesSpider(scrapy.Spider):

    name = 'player_details'

    custom_settings = sofifa_settings(name=name, proxies=proxies, user_agent=user_agent, collection='player_details',
                                      validator='PlayerItem')
    client = MongoClient('localhost', 27017)
    db = client.sofifa
    collection = db.player_urls

    urls = [x["player_page"] for x in collection.find({'player_page': {'$exists': 'true'}})]

    def start_requests(self):

        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        self.crawler.stats.set_value('pages_to_visit', len(self.urls))

        loader = ItemLoader(item=SofifaItem(), response=response)
        col_4_loader = loader.nested_xpath(".//div[@class='column col-4 text-center']")

        # GENERAL PLAYER INFORMATION

        loader.add_xpath('id', ".//div[@class='info']/h1/text()")
        loader.add_xpath('name', ".//div[@class='info']/h1/text()")
        loader.add_xpath('full_name', ".//div[@class='meta']/text()")
        loader.add_xpath('age', ".//div[@class='meta']/text()/following-sibling::text()[last()]")
        loader.add_xpath('dob', ".//div[@class='meta']/text()/following-sibling::text()[last()]")
        loader.add_xpath('height', ".//div[@class='meta']/text()/following-sibling::text()[last()]")
        loader.add_xpath('weight', ".//div[@class='meta']/text()/following-sibling::text()[last()]")
        loader.add_xpath('nationality', ".//div[@class='meta']/a/@title")

        # GENERAL PLAYER STATS

        loader.add_xpath('preferred_foot', "(.//label[text()='Preferred Foot']/following::text())[1]")
        loader.add_xpath('international_reputation',
                         "(.//label[text()='International Reputation']/following::text())[1]")
        loader.add_xpath('weak_foot', "(.//label[text()='Weak Foot']/following::text())[1]")
        loader.add_xpath('skill_moves', "(.//label[text()='Skill Moves']/following::text())[1]")
        loader.add_xpath('work_rate', "(.//label[text()='Work Rate']/following::span/text())[1]")
        loader.add_xpath('body_type', "(.//label[text()='Body Type']/following::span/text())[1]")
        loader.add_xpath('real_face', "(.//label[text()='Real Face']/following::span/text())[1]")

        # CLUB/TEAM INFORMATION

        col_4_loader.add_xpath('value', "following::text()[contains(., 'Value')]/following::span[1]/text()")
        col_4_loader.add_xpath('wage', "following::text()[contains(., 'Wage')]/following::span[1]/text()")
        loader.add_xpath('release_clause', "(.//label[text()='Release Clause']/following::span/text())[1]")
        loader.add_xpath('club_name', "(.//ul[@class='pl']//a/text())[1]")
        loader.add_xpath('club_rating', ".//div[@class='column col-4'][3]/ul/li[2]/span/text()")
        loader.add_xpath('club_position', "(.//label[text()='Position']/following::text()[1])[1]")
        loader.add_xpath('club_jersey_number',
                         "(.//label[text()='Jersey Number']/following::text()[1])[1]")
        loader.add_xpath('club_join_date',
                         ".//label[text()='Joined']/following::text()[1]")
        loader.add_xpath('loaned_from', ".//label[text()='Loaned From']/following::a[1]/text()")
        loader.add_xpath('club_contract_end_date',
                         ".//label[text()='Contract Valid Until']/following::text()[1]")
        loader.add_xpath('team_name', "(.//ul[@class='pl']//a/text())[2]")
        loader.add_xpath('team_rating', ".//div[@class='column col-4'][4]/ul/li[2]/span/text()")
        loader.add_xpath('team_position', "(.//label[text()='Position']/following::text()[1])[2]")
        loader.add_xpath('team_jersey_number',
                         "(.//label[text()='Jersey Number']/following::text()[1])[2]")

        # PLAYER GAME STATS

        loader.add_xpath('overall_rating',
                         "(.//div[@class='column col-4 text-center']"
                         "/preceding::text()[contains(.,'Overall Rating')])[2]/following::span[1]/text()")
        col_4_loader.add_xpath('potential_rating', "following::text()[contains(., 'Potential')]/following::span[1]"
                                                   "/text()")
        loader.add_xpath('positions', ".//div[@class='meta']/span/text()")
        loader.add_xpath('unique_attributes', ".//div[@class='mt-2']/a/text()")

        if 'GK' in response.xpath(".//div[@class='meta']/span/text()").getall():

            loader.add_xpath('DIV',
                             ".//div[@class='wrapper']//script[contains(text(), 'var overallRating')]/text()")
            loader.add_xpath('HAN',
                             ".//div[@class='wrapper']//script[contains(text(), 'var overallRating')]/text()")
            loader.add_xpath('KIC',
                             ".//div[@class='wrapper']//script[contains(text(), 'var overallRating')]/text()")
            loader.add_xpath('REF',
                             ".//div[@class='wrapper']//script[contains(text(), 'var overallRating')]/text()")
            loader.add_xpath('SPD',
                             ".//div[@class='wrapper']//script[contains(text(), 'var overallRating')]/text()")
            loader.add_xpath('POS',
                             ".//div[@class='wrapper']//script[contains(text(), 'var overallRating')]/text()")

        else:

            loader.add_xpath('PAC',
                             ".//div[@class='wrapper']//script[contains(text(), 'var overallRating')]/text()")
            loader.add_xpath('SHO',
                             ".//div[@class='wrapper']//script[contains(text(), 'var overallRating')]/text()")
            loader.add_xpath('PAS',
                             ".//div[@class='wrapper']//script[contains(text(), 'var overallRating')]/text()")
            loader.add_xpath('DRI',
                             ".//div[@class='wrapper']//script[contains(text(), 'var overallRating')]/text()")
            loader.add_xpath('DEF',
                             ".//div[@class='wrapper']//script[contains(text(), 'var overallRating')]/text()")
            loader.add_xpath('PHY',
                             ".//div[@class='wrapper']//script[contains(text(), 'var overallRating')]/text()")

        # PLAYER DETAILED STATS

        loader.add_xpath('crossing', "(.//span[../span='Crossing']/text())[1]")
        loader.add_xpath('finishing', "(.//span[../span='Finishing']/text())[1]")
        loader.add_xpath('heading_accuracy', "(.//span[../span='Heading Accuracy']/text())[1]")
        loader.add_xpath('short_passing', "(.//span[../span='Short Passing']/text())[1]")
        loader.add_xpath('volleys', "(.//span[../span='Volleys']/text())[1]")
        loader.add_xpath('aggression', "(.//span[../span='Aggression']/text())[1]")
        loader.add_xpath('interceptions', "(.//span[../span='Interceptions']/text())[1]")
        loader.add_xpath('positioning', "(.//span[../span='Positioning']/text())[1]")
        loader.add_xpath('vision', "(.//span[../span='Vision']/text())[1]")
        loader.add_xpath('penalties', "(.//span[../span='Penalties']/text())[1]")
        loader.add_xpath('composure', ".//li[contains(text(), 'Composure')]/span/text()")
        loader.add_xpath('dribbling', "(.//span[../span='Dribbling']/text())[1]")
        loader.add_xpath('curve', "(.//span[../span='Curve']/text())[1]")
        loader.add_xpath('fk_accuracy', "(.//span[../span='FK Accuracy']/text())[1]")
        loader.add_xpath('long_passing', "(.//span[../span='Long Passing']/text())[1]")
        loader.add_xpath('ball_control', "(.//span[../span='Ball Control']/text())[1]")
        loader.add_xpath('marking', "(.//span[../span='Marking']/text())[1]")
        loader.add_xpath('standing_tackle', "(.//span[../span='Standing Tackle']/text())[1]")
        loader.add_xpath('sliding_tackle', "(.//span[../span='Sliding Tackle']/text())[1]")
        loader.add_xpath('acceleration', "(.//span[../span='Acceleration']/text())[1]")
        loader.add_xpath('sprint_speed', "(.//span[../span='Sprint Speed']/text())[1]")
        loader.add_xpath('agility', "(.//span[../span='Agility']/text())[1]")
        loader.add_xpath('reactions', "(.//span[../span='Reactions']/text())[1]")
        loader.add_xpath('balance', "(.//span[../span='Balance']/text())[1]")
        loader.add_xpath('gk_diving', ".//li[contains(text(), 'GK Diving')]/span/text()")
        loader.add_xpath('gk_handling', ".//li[contains(text(), 'GK Handling')]/span/text()")
        loader.add_xpath('gk_kicking', ".//li[contains(text(), 'GK Kicking')]/span/text()")
        loader.add_xpath('gk_positioning', ".//li[contains(text(), 'GK Positioning')]/span/text()")
        loader.add_xpath('gk_reflexes', ".//li[contains(text(), 'GK Reflexes')]/span/text()")
        loader.add_xpath('shot_power', "(.//span[../span='Shot Power']/text())[1]")
        loader.add_xpath('jumping', "(.//span[../span='Jumping']/text())[1]")
        loader.add_xpath('stamina', "(.//span[../span='Stamina']/text())[1]")
        loader.add_xpath('strength', "(.//span[../span='Strength']/text())[1]")
        loader.add_xpath('long_shots', "(.//span[../span='Long Shots']/text())[1]")
        loader.add_xpath('traits', ".//h5[text()='Traits']/following-sibling::ul/li/span/text()")

        # PLAYER REAL OVERALL RATING (POSITIONAL STATS)

        loader.add_xpath('LS', "(.//div[../div='LS']/following::text())[1]")
        loader.add_xpath('ST', "(.//div[../div='ST']/following::text())[1]")
        loader.add_xpath('RS', "(.//div[../div='RS']/following::text())[1]")
        loader.add_xpath('LW', "(.//div[../div='LW']/following::text())[1]")
        loader.add_xpath('LF', "(.//div[../div='LF']/following::text())[1]")
        loader.add_xpath('CF', "(.//div[../div='CF']/following::text())[1]")
        loader.add_xpath('RF', "(.//div[../div='RF']/following::text())[1]")
        loader.add_xpath('RW', "(.//div[../div='RW']/following::text())[1]")
        loader.add_xpath('LAM', "(.//div[../div='LAM']/following::text())[1]")
        loader.add_xpath('CAM', "(.//div[../div='CAM']/following::text())[1]")
        loader.add_xpath('RAM', "(.//div[../div='RAM']/following::text())[1]")
        loader.add_xpath('LM', "(.//div[../div='LM']/following::text())[1]")
        loader.add_xpath('LCM', "(.//div[../div='LCM']/following::text())[1]")
        loader.add_xpath('CM', "(.//div[../div='CM']/following::text())[1]")
        loader.add_xpath('RCM', "(.//div[../div='RCM']/following::text())[1]")
        loader.add_xpath('RM', "(.//div[../div='RM']/following::text())[1]")
        loader.add_xpath('LWB', "(.//div[../div='LWB']/following::text())[1]")
        loader.add_xpath('LDM', "(.//div[../div='LDM']/following::text())[1]")
        loader.add_xpath('CDM', "(.//div[../div='CDM']/following::text())[1]")
        loader.add_xpath('RDM', "(.//div[../div='RDM']/following::text())[1]")
        loader.add_xpath('RWB', "(.//div[../div='RWB']/following::text())[1]")
        loader.add_xpath('LB', "(.//div[../div='LB']/following::text())[1]")
        loader.add_xpath('LCB', "(.//div[../div='LCB']/following::text())[1]")
        loader.add_xpath('CB', "(.//div[../div='CB']/following::text())[1]")
        loader.add_xpath('RCB', "(.//div[../div='RCB']/following::text())[1]")
        loader.add_xpath('RB', "(.//div[../div='RB']/following::text())[1]")

        # COMMUNITY INFORMATION

        loader.add_xpath('followers', "(.//div[@class='operation mt-2']/a/text()[contains(.,'Follow')]"
                                      "/following::span)[1]/text()")
        loader.add_xpath('likes', "(.//div[@class='operation mt-2']/a/text()[contains(.,'Like')]"
                                  "/following::span)[1]/text()")
        loader.add_xpath('dislikes', "(.//div[@class='operation mt-2']/a/text()[contains(.,'Dislike')]"
                                     "/following::span)[1]/text()")

        # MEDIA

        loader.add_xpath('face_img', ".//div/div/article/div/img//@data-src")
        loader.add_xpath('flag_img', ".//div[@class='meta']/a/img/@data-src")
        loader.add_xpath('club_logo_img', "(.//div/ul/li/figure/img/@data-src)[1]")
        loader.add_xpath('team_logo_img', "(.//div/ul/li/figure/img/@data-src)[2]")

        self.logger.info(f'Parse function called on {response.url}')

        self.logger.info(f"Currently on page {self.crawler.stats.get_value('page_counter')} out of "
                         f"{self.crawler.stats.get_value('pages_to_visit')}")

        # TODO: enable continued logging of page_counter after a pause/resume.
        self.crawler.stats.inc_value(key='page_counter', count=1, start=0)

        print(response.request.headers['User-Agent'])
        print(f"{self.crawler.stats.get_value('page_counter')} out of {self.crawler.stats.get_value('pages_to_visit')}")

        yield loader.load_item()
