from enum import Enum
import re
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Comment

import logging
logger = logging.getLogger(__name__)
bs4_logger = logging.getLogger("bs4.dammit")
bs4_logger.setLevel(logging.INFO)

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
    PRAJAVANI='prajavani'
    VIJAYAKARNATAKA='vijaykarnataka'
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
        text_1 = ""
        if div_article_text is not None:
            span = div_article_text.find("span")
            if span is not None and span.text is not None:
                text_1 = span.get_text(" ").strip()
        
        # Alternate way 1
        story_content = self.soup.find("div", id="storyContent")
        text_2 = ""
        if story_content is not None:
            # Remove the divs with class="author_txt" and class="agency_txt"
            author_txt = story_content.find("div", class_="author_txt")
            if author_txt is not None:
                author_txt.clear()
            agency_txt = story_content.find("div", class_="agency_txt")
            if agency_txt is not None:
                agency_txt.clear()

            if story_content.text is not None:
                text_2 = story_content.get_text(" ").strip()

        # If one of these have some non-empty text, return the longest one
        if len(text_1) != 0 or len(text_2) != 0:
            if len(text_1) > len(text_2):
                return text_1
            else:
                return text_2

        # Alternate way 2
        article_text = self.soup.find('div', class_="article_text")
        if article_text is not None:
            span = article_text.find('span')
            if span is not None and span.text is not None:
                return span.get_text(" ")
            
        # Last option
        return None

class PrajavaniParser():
    """Interface that declares various extraction methods"""
    def __init__(self, html_text, url):
        self.soup = BeautifulSoup(html_text, "html.parser")
        self.url = url

    def is_valid_article_page(self):
        if self.soup.head is None:
            conf_parser.error_logger.error("Invalid Article! Couldn't detect article validity:{}".format(self.url))
            return False

        # Alternate way 1
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

        # Alternate way 2 (A bit hacky way)
        article_title = self.soup.find("div", class_="pj-article__title")
        if article_title is not None and len(str(article_title.text).strip()) > 5:
            return True

        # Last option
        logger.debug('Page does not seem to contain article: {}'.format(self.url))
        # For debugging these pages
        conf_parser.error_logger.error("Invalid Article! {}".format(self.url))
        return False

    def extract_title(self):
        # Most commonly found title
        pj_article_title = self.soup.find("div", attrs={"class": "pj-article__title"})
        if pj_article_title is not None:
            h1 = pj_article_title.find("h1")
            if h1 is not None:
                return h1.text
            else:
                return pj_article_title.text

        # Alternate way 1
        meta = self.soup.find("meta", attrs={"property": "og:title"})
        if meta is not None and "content" in meta.attrs:
            return meta["content"]
        
        # Last option
        return self.soup.find("title").string

    def extract_description(self):
        # Most commonly found in meta
        meta_desc = self.soup.find("meta", attrs={"name": "description"})
        if meta_desc is not None and "content" in meta_desc.attrs:
            return meta_desc["content"]

        # Alternate way 1
        meta_desc = self.soup.find("meta", attrs={"property": "og:description"})
        if meta_desc is not None and "content" in meta_desc.attrs:
            return meta_desc["content"]        
        
        # Last option
        return None

    def extract_keywords(self):
        # Most commonly found
        div_article_tags = self.soup.find("div", class_=re.compile("pj-article__tags.*"))
        if div_article_tags is not None:
            return div_article_tags.get_text(",")

        # Alternate way 1
        news_keywords = self.soup.find("meta", attrs={"name": "keywords"})
        if news_keywords is not None and "content" in news_keywords.attrs:
            return news_keywords["content"]

        return None

    def extract_publish_date(self):
        # Most commonly found
        authors_date_section = self.soup.find("div", class_="pj-article__detail__authors__date-section")
        if authors_date_section is not None:
            time_tag = authors_date_section.find("time")
            if time_tag is not None:
                return time_tag.string

        # Alternate way 1
        article_date_published = self.soup.find("div", class_=re.compile("pj-article__detail__date-published.*"))
        if article_date_published is not None:
            time_tag = article_date_published.find("time")
            if time_tag is not None:
                return time_tag.string

        # Last option
        meta_publish_time = self.soup.find("meta", attrs={"property": "article:published_time"})
        if meta_publish_time is not None and "content" in meta_publish_time.attrs:
            return meta_publish_time["content"]

        return None

    def extract_article_text(self):
        # Extract text from all <p>
        def __get_article_text(body):
            article_text = ""
            for ps in body.find_all("p"):
                para_text = ps.get_text(" ")
                # Empty string, ignore
                if len(str(para_text).strip()) == 0:
                    continue

                # If the text in this ps is same as that of first <a>, then this 'ps'
                #  does not contain anything else, so ignore it
                first_a = ps.find("a")
                if first_a is not None and len(para_text) <= len(first_a.text):
                    continue

                # Clear the intermediate links
                if "ಇದನ್ನೂ ಓದಿ" in para_text or "ಇನ್ನಷ್ಟು..." in para_text:
                    all_a = ps.find_all("a")
                    for a in all_a:
                        # Remove the anchor text
                        a.clear()
                    # Recapture the whole text
                    para_text = ps.get_text(" ")
                    # Remove special texts
                    para_text = para_text.replace("ಇದನ್ನೂ ಓದಿ:", "") \
                        .replace("ಇದನ್ನೂ ಓದಿ...", "") \
                        .replace("ಇದನ್ನೂ ಓದಿ", "") \
                        .replace("ಇನ್ನಷ್ಟು...", "")

                article_text = article_text + para_text + "\n"
            return article_text

        # Most commonly found and found only in this!
        article_content = self.soup.find("div", class_="pj-article__content")
        if article_content is not None:
            return __get_article_text(article_content)
        
        # Alternate way 1
        article_field = self.soup.find("div", class_=re.compile("field field-name-body"))
        if article_field is not None:
            return __get_article_text(article_field)

        # Last option
        return None

class VijayakarnatakaParser():
    """Interface that declares various extraction methods"""
    def __init__(self, html_text, url):
        self.soup = BeautifulSoup(html_text, "html.parser")
        self.url = url

    def is_valid_article_page(self):
        # If URL path has '/tech/' or /video/ then drop this page
        str_url = str(self.url)
        if '/tech/' in str_url or '/video/' in str_url:
            logger.info("Ignoring {} as it is a tech/video article!".format(self.url)) 
            return False

        article_div = self.soup.find("div", class_="article")
        if article_div is not None:
            article_div = article_div.find("div", class_="section1")
            if article_div is not None:
                # Has some decent amount of text
                if len(article_div.text) > 99:
                    return True

        if self.soup.head is None:
            conf_parser.error_logger.error("Invalid Article! Couldn't detect article validity:{}".format(self.url))
            return False

        # Alternate way 1
        page_type = self.soup.head.find('meta', attrs={"name": "og:type"})
        if page_type is not None:
            og_type = page_type['content']
            logger.debug('Og Type: {}'.format(og_type))
            # Check the content type
            if og_type == 'article':
                return True
        # Alternative way 2
        page_type = self.soup.head.find('meta', attrs={"property": "og:type"})
        if page_type is not None:
            og_type = page_type['content']
            logger.debug('Og Type: {}'.format(og_type))
            # Check the content type
            if og_type == 'article':
                return True
            
        # Last option
        logger.debug('Page does not seem to contain article: {}'.format(self.url))
        # For debugging these pages
        conf_parser.error_logger.error("Invalid Article! {}".format(self.url))
        return False

    def extract_title(self):
        # Most commonly found title
        story_article = self.soup.find("div", attrs={"class": "story-article"})
        if story_article is not None:
            h1 = story_article.find("h1")
            if h1 is not None:
                return h1.text

        content_area = self.soup.find("div", id=re.compile("contentarea_*"))
        if content_area is not None:
            h1 = content_area.find("h1")
            if h1 is not None:
                return h1.text

        # Alternate way 1
        meta = self.soup.find("meta", attrs={"property": "og:title"})
        if meta is not None and "content" in meta.attrs:
            return meta["content"]

        # Last option
        ttl = self.soup.find("title")
        if ttl is not None:
            return ttl.string
        else:
            # Blindly return the first <h1>
            return self.soup.find("h1").text

    def extract_description(self):
        # Most commonly found in meta
        enable_read_more_div = self.soup.find("div", attrs={"class": "enable-read-more"})
        if enable_read_more_div is not None:
            h2 = enable_read_more_div.find("h2")
            if h2 is not None:
                return h2.text

        # Alternate way 1
        content_area = self.soup.find("div", id=re.compile("contentarea_*"))
        if content_area is not None:
            h2 = content_area.find("h2")
            if h2 is not None:
                return h2.text

        # Alternate way 2
        meta_desc = self.soup.find("meta", attrs={"name": "description"})
        if meta_desc is not None and "content" in meta_desc.attrs:
            return meta_desc["content"]

        # Alternate way 3
        meta_desc = self.soup.find("meta", attrs={"property": "og:description"})
        if meta_desc is not None and "content" in meta_desc.attrs:
            return meta_desc["content"]

        # Last option
        return None

    def extract_keywords(self):
        def get_keywords_from_links(keyword_div):
            cont_div = keyword_div.find("div", class_="nowarp_content")
            if cont_div is not None:
                return None
            all_keys = []
            for sp in cont_div.find_all("span"):
                if sp.text is not None:
                    all_keys.append(sp.text)
            if len(all_keys) > 0:
                ','.join(all_keys)
            else:
                return None

        # Most commonly found
        div_keywords = self.soup.find("div", class_="keywords")
        if div_keywords is not None:
            keys = get_keywords_from_links(div_keywords)
            if keys is not None:
                return keys

        div_keywords = self.soup.find("div", class_="keywords_wrap")
        if div_keywords is not None:
            keys = get_keywords_from_links(div_keywords)
            if keys is not None:
                return keys

        # Alternate way 1
        news_keywords = self.soup.find("meta", attrs={"name": re.compile("[kK]eywords")})
        if news_keywords is not None and "content" in news_keywords.attrs:
            return news_keywords["content"]

        return None

    def extract_publish_date(self):
        # Most commonly found
        datePublished_meta = self.soup.find("meta", attrs={"itemprop": "datePublished"})
        if datePublished_meta is not None and "content" in datePublished_meta.attrs:
            return datePublished_meta["content"]

        # Alternate way 1
        time_span = self.soup.find("span", class_="time")
        if time_span is not None:
            return time_span.text

        # Alternate way 2
        datetime_div = self.soup.find("div", class_="article_datetime")
        if datetime_div is not None:
            time_tag = datetime_div.find("time")
            if time_tag is not None:
                return time_tag.text
            else:
                # Remove the <span>
                dtsp = datetime_div.find("span")
                if dtsp is not None:
                    dtsp.clear()
                return datetime_div.text

        return None

    def is_line_break(self, element):
        return (element == '\n' or element.name == 'br')

    def extract_article_text(self):
        # Extract text from all <p>
        def __get_article_text(article_body):
            children = list(article_body.children)
            article_text = ""
            for i,ch in enumerate(children):
                # Ignore ad and br tags
                if ch.name == 'ad' or ch.name == 'br':
                    #print(str(ch))
                    pass
                # If it is a plain text
                elif type(ch) is NavigableString:
                    txt = str(ch)
                    if len(txt) >= 1:
                        article_text = article_text + ' ' + txt
                else:
                    # It could be a <br/> or <a/>
                    # if it is an <a/>, check previous and next tags
                    if ch.name == 'a':
                        # Starts with <a/>
                        if i == 0:
                            article_text = article_text + ch.text
                        # Ends with <a/>
                        elif i == len(children)-1:
                            pass
                        # In-between <br/> tags
                        else:
                            # A <a> tag surrounded by <br/>
                            if self.is_line_break(children[i-1]) and self.is_line_break(children[i+1]):
                                pass
                            else:
                                article_text = article_text + ch.text
                    # Div tag with image or ad, ignore it
                    elif ch.name == 'div':
                        cls_str = ' '.join(ch["class"])
                        if 'img' in cls_str or 'ad' in cls_str:
                            pass
                        else:
                            article_text = article_text + ch.text

                    # Any other tag, just add the text
                    else:
                        article_text = article_text + ch.text

            # End of for
            return article_text

        # Most commonly found and found only in this!
        article_content = self.soup.find("article", class_="story-content")
        if article_content is not None:
            return __get_article_text(article_content)

        # Alternate way 1
        article_div = self.soup.find("div", class_="article")
        if article_div is not None:
            article_div = article_div.find("div", class_="section1")
            if article_div is not None:
                norm_div = article_div.find("div", class_="Normal")
                if norm_div is not None:
                    children = list(norm_div.children)
                    article_text = ""
                    for i,child in enumerate(children):
                        # Ignore the div children
                        if child.name == "div" or type(child) == Comment:
                            pass
                        else:
                            if type(child) is NavigableString:
                                article_text = article_text + str(child)
                            # if it is an <a/>, check previous and next tags
                            elif child.name == 'a':
                                # Starts with <a/>
                                if i == 0:
                                    article_text = article_text + child.text
                                # Ends with <a/>
                                elif i == len(children)-1:
                                    pass
                                # In-between <br/> tags
                                else:
                                    # A <a> tag surrounded by <br/>
                                    if self.is_line_break(children[i-1]) and self.is_line_break(children[i+1]):
                                        pass
                                    else:
                                        article_text = article_text + child.get_text(" ").strip()
                            else:
                                article_text = article_text + child.get_text(" ").strip()
                    # End of for
                    return article_text
                # If no "Normal" div is found 
                else:
                    return article_div.get_text(" ").strip()

        # Last option
        return None
    
def test_knd(base_path, files):
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
    test_knd(base_path, files)

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
        '2021/union-budget-2021-fiscal-deficit-estimated-at-95-of-gdp-for-this-year-438647.html',
        'small_article/how-will-india-pakistan-conflict-impact-economy-countries-that-support-india-here-is-all-you-need-to-know-333612.html',
        'small_article/is-donald-trump-gearing-up-for-currency-war-here-is-all-you-need-to-know-342071.html'
        ]
    test_knd(base_path, files)

def test_prj(base_path, files):
    for html_file_path in files:
        print(html_file_path)
        html_text = open(base_path + html_file_path, 'rb').read()
        parser = PrajavaniParser(html_text, 'http://'+html_file_path)
        if parser.is_valid_article_page():
            logger.info('Title: {}'.format(parser.extract_title()))
            logger.info('Keywords: {}'.format(parser.extract_keywords()))
            logger.info('Description: {}'.format(parser.extract_description()))
            logger.info('Publish Date: {}'.format(parser.extract_publish_date()))
            logger.info('Article Text: {}'.format(parser.extract_article_text()))
        else:
            logger.warning('Not a valid article page!')
        print('-'*50)

def test_run3():
    base_path = '/home/adiga/my_work/kannada-news-dataset/crawling/test/www.prajavani.net/'
    files = ['index.html',
        'article-on-ooty-and-kannada-language-796882.html',
        'rajnath-singh-says-india-no-longer-a-weak-country-736381.html',
        '2018/LzIwMTgvMDkvMDEvNTY5OTAz_index.html',
        '2018/LzIwMTgvMDUvMjYvNTQ1MDg3_index.html',
        '2018/LzIwMTgvMDYvMjcvNTUyMjA2_index.html',
        '2019/ban-unions-strike-664152.html',
        '2019/knowledge-from-research-694131.html',
        '2019/mla-653311.html',
        '2020/joe-biden-wins-new-jersey-and-new-york-donald-trump-registering-early-wins-in-key-states-776310.html',
        '2021/twiter-campaign-to-kodagu-forest-minister-813774.html',
        'agri-college-quota-misuse-637140.html',
        'cashewnut-in-north-karnataka-762670.html',
        'kodagu-falls-664286.html',
        'missing_article/flood-relief-fund_index.html',
        'missing_article/gsqjgs43gsq8_index.html',
        'missing_article/chikkamagalur_index.html',
        'missing_article/couple-death_index.html',
        'missing_article/shrimant-patil_index.html',
        'missing_article/article-features_index.html',
        'missing_article/cartoon-prajavani-chinakurali-coronavirus-covid-vaccine-bjp-773564.html',
        'missing_article/cartoon-covid-19-and-air-pollution-754793.html',
        'small_article/LzIwMTgvMTAvMDgvNTc5NDkx_index.html',
        'small_article/no-surprise-if-shiv-sena-comes-to-power-in-delhi-too-says-sanjay-raut-685666.html'
        ]

    test_prj(base_path, files)
    
def test_vij(base_path, files):
    for html_file_path in files:
        print(html_file_path)
        html_text = open(base_path + html_file_path, 'rb').read()
        parser = VijayakarnatakaParser(html_text, 'http://'+html_file_path)
        if parser.is_valid_article_page():
            logger.info('Title: {}'.format(parser.extract_title()))
            logger.info('Keywords: {}'.format(parser.extract_keywords()))
            logger.info('Description: {}'.format(parser.extract_description()))
            logger.info('Publish Date: {}'.format(parser.extract_publish_date()))
            logger.info('Article Text: {}'.format(parser.extract_article_text()))
        else:
            logger.warning('Not a valid article page!')
        print('-'*50)

def test_run4():
    base_path = '/home/adiga/my_work/kannada-news-dataset/crawling/test/vijayakarnataka.com/'
    files = [
        'non-html/76331855.cms.html',
        'non-html/B08L5WS5JB?tag=vk_web_pdp_rhsbrandwidget-21&linkCode=ogi&th=1&psc=1&price=129900.0&title=Apple iPhone 12 Pro Max&amz_ga=undefined_129900.0.html',
        'non-html/69793401.cms.html',
        'photo/msid-78486461.cms.html',
        'photo/75670970.cms.html',
        'education/67883582.cms.html',
        'sports/70704765.cms.html',
        'sports/78627794.cms.html',
        'jobs/71230807.cms.html',
        'jobs/73155282.cms.html',
        'district/64781149.cms.html',
        'news/71393318.cms.html',
        'news/71635430.cms.html',
        'video/78478608.cms.html',
        'video/71864402.cms.html',
        'tv/80707311.cms.html',
        'tv/76670998.cms.html',
        'html/Dell-Vostro-15-3568-A553113UIN9-Laptop-Core-i5-7th-Gen8-GB1-TBLinux2-GB_index.html',
        'tech/Dell-Inspiron-14-3467-A561201UIN9-Laptop-Core-i3-6th-Gen4-GB1-TBLinux_index.html',
        'tech/RX-5600M120-Hz-G5-5505-Gaming-Laptop-156-inch-Silver-25-kg-D560323HIN9S_index.html',
        'topics/ರಾಧಿಕಾ-ಹೆಗಡೆ-ಹುಳಗೋಳ_index.html'
        ]

    test_vij(base_path, files)

if __name__ == '__main__':
    conf_parser.log_config
    # test_run1() 
    # test_run2() 
    # test_run3() 

    # Vijayakarnataka Tests
    test_run4()