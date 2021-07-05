from enum import Enum
import re
from bs4 import BeautifulSoup
import logging
logger = logging.getLogger(__name__)

import conf_parser

class HtmlParserI():
    """Interface that declares various extraction methods"""
    def is_valid_article_page():
        pass
    def extract_title():
        pass
    def extract_description():
        pass
    def extract_keywords():
        pass
    def extract_publish_date():
        pass
    def extract_article_text():
        pass

class Website(Enum):
    KANNADAPRABHA='kannadaprabha'
    # TODO Other websites go here

class KannadaPrabhaParser(HtmlParserI):
    def __init__(self, html_text, url):
        self.soup = BeautifulSoup(html_text, "html.parser")
        self.url = url
        # For verifying
        # logger.debug('Valid article page: {}'.format(self.is_valid_article_page()))

    def is_valid_article_page(self):
        if self.soup.head is None:
            conf_parser.error_logger.error("Invalid Article! Couldn't detect article validity:{}".format(self.url))
            return False

        page_type = self.soup.head.find_all('meta', attrs={"property": "og:type"})
        if len(page_type) == 1:
            page_type = page_type[0]
            og_type = page_type['content']
            logger.debug('Og Type: {}'.format(og_type))
            # Check the content type
            if og_type == 'article':
                return True
            else:
                logger.debug("Og Type is not 'article' for this url!")

        else:
            logger.debug('Page does not seem to contain article: {}'.format(self.url))

        # For debugging these pages
        conf_parser.error_logger.error("Invalid Article! {}".format(self.url))
        return False


    def extract_title(self):
        # Most commonly found title
        div_article_headline = self.soup.find("div", attrs={"class": "div_article_headline"})
        if div_article_headline is not None:
            span = div_article_headline.find("span")
            return span.string

        # Alternate way 1 
        article_head = self.soup.find("h1", attrs={"class": "ArticleHead"})
        if article_head is not None:
            return article_head.string

        # Alternate way 2
        div_headline = self.soup.find('div', class_="article_headline")
        if div_headline is not None:
            span = div_headline.find("span")
            return span.string

        # Alternate way 3
        meta = self.soup.find("meta", attrs={"property": "og:title"})
        if meta is not None and "content" in meta.attrs:
            return meta["content"]
        
        # Last option
        return self.soup.find("title").string
        
    def extract_keywords(self):
        # Most commonly found in meta
        news_keywords = self.soup.find("meta", attrs={"name": "news_keywords"})
        if news_keywords is not None and "content" in news_keywords.attrs:
            return news_keywords["content"]
        
        # Alternate way
        keyword = self.soup.find('div', class_="article_topic")
        if keyword is not None and keyword.span is not None:
            return keyword.span.string
        
        # Last option
        return None

    def extract_description(self):
        # Most commonly found in meta
        meta_desc = self.soup.find("meta", attrs={"property": "og:description"})
        if meta_desc is not None and "content" in meta_desc.attrs:
            return meta_desc["content"]
        
        # Last option
        return None

    def extract_publish_date(self):
        # Most commonly found
        div_article_dateline = self.soup.find("div", class_="div_article_dateline")
        if div_article_dateline is not None:
            spans = div_article_dateline.find_all("span")
            if spans is not None and len(spans) > 0:
                return spans[0].string

        # Alternate way 1: Find p with class="ArticlePublish margin-bottom-10"
        article_publish = self.soup.find("p", class_=re.compile("ArticlePublish.*"))
        if article_publish is not None:
            spans = article_publish.find_all("span")
            if spans is not None and len(spans) > 0:
                return spans[0].string
        
        # Alternate way 2
        dateline = self.soup.find('div', class_="article_dateline")
        if dateline is not None:
            spans = dateline.find_all("span")
            if spans is not None and len(spans) > 0:
                return spans[0].string

        # Last option
        return None

    def extract_article_text(self):
        # WARN:: Returns the plain text, AFTER REMOVING all the children tags and paragraph layouts

        # Most commonly found
        div_article_text = self.soup.find("div", class_="div_article_text")
        if div_article_text is not None:
            span = div_article_text.find("span")
            if span is not None and span.text is not None:
                return span.text
        
        # Alternate way 1
        story_content = self.soup.find("div", id="storyContent")
        if story_content is not None:
            # Remove the divs with class="author_txt" and class="agency_txt"
            author_txt = story_content.find("div", class_="author_txt")
            if author_txt is not None:
                author_txt.clear()
            agency_txt = story_content.find("div", class_="agency_txt")
            if agency_txt is not None:
                agency_txt.clear()

            if story_content.text is not None:
                return story_content.text

        # Alternate way 2
        article_text = self.soup.find('div', class_="article_text")
        if article_text is not None:
            span = article_text.find('span')
            if span is not None and span.text is not None:
                return span.text
            
        # Last option
        return None

    
def test(base_path, files):
    for html_file_path in files:
        print(html_file_path)
        html_text = open(base_path + html_file_path, 'rb').read()
        parser = KannadaPrabhaParser(html_text, 'http://'+html_file_path)
        if parser.is_valid_article_page():
            logger.info('Title: {}'.format(parser.extract_title()))
            logger.info('Keywords: {}'.format(parser.extract_keywords()))
            logger.info('Description: {}'.format(parser.extract_description()))
            logger.info('Publish Date: {}'.format(parser.extract_publish_date()))
            logger.info('Article Text: {}'.format(parser.extract_article_text()))
        else:
            logger.warning('Not a valid article page!')
        print('-'*50)

def test_run1():
    base_path = '/home/adiga/my_work/kannada-news-dataset/crawling/snapshot_download/kannadaprabha/run1/websites/'
    files = [
        'www.kannadaprabha.com/districts/bangalore/ನಂಜುಂಡಪ್ಪ-ವರದಿ-ಜಾರಿಯಾಗಲಿ/93790.html',
        'www.kannadaprabha.com/column/hachcha-hasiru/index.html',
        'www.kannadaprabha.com/columns/ರಣಾಂಗಣದ-ನಯ-ನಾಜೂಕು-ಹುಟ್ಟಿಸಿರುವ-ಸಂದೇಹ/43092.html',
        'www.kannadaprabha.com/astrology/ಚಿರ-ಯೌವ್ವನಿಗರಾಗಿ/85409.html'
        ]
    test(base_path, files)

def test_run2():
    base_path = '/home/adiga/my_work/kannada-news-dataset/crawling/test/www.kannadaprabha.com/'
    files = ['index.html',
        '2014/bangladesh-election/244380.html',
        '2015/how-to-perform-gowri-puja-at-home-258095.html',
        '2016/karnataka-cm-siddaramaiah-looking-at-please-all-budget-now/271152.html',
        '2017/karnataka-state-budget-2017-18-allocations-for-health-department/291852.html',
        '2017/what-is-universal-basic-income-here-are-the-details/289532.html',
        '2018/loan-waiver-or-not-meet-our-demands-organisations/319541.html',
        '2019/karnataka-budget-2019-jetty-to-be-constructed-at-malpe/333491.html',
        '2020/budget-session-of-parliament-to-commence-on-january-31-409980.html',
        '2021/union-budget-2021-fiscal-deficit-estimated-at-95-of-gdp-for-this-year-438647.html'
        ]
    test(base_path, files)
    
if __name__ == '__main__':
    conf_parser.log_config
    test_run1() 
    test_run2() 