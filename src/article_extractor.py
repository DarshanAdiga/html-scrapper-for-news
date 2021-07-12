import os
import re
import traceback
import time
from es_storage import ESStorage
from urllib.parse import ParseResult, urljoin, urlparse
import logging
logger = logging.getLogger(__name__)

from storage import StorageI
from es_doc_maker import make_article_doc
import conf_parser
from html_parser import Website, KannadaPrabhaParser, PrajavaniParser

class URLLookup():
    """Helper class that defines url-lookup. Currently, it uses in-memory set for lookup.
    """
    def __init__(self, article_storage: StorageI):
        self.article_storage = article_storage
        self.extracted_url_set = set()
        self.__load_url_index()

    def __load_url_index(self):
        # URLs from which article has been extracted already
        extracted_url_itr = []
        if self.article_storage.storage_exists():
            es_query_extracted = {
                "_source": False,
                "query": {"bool": {"must": [{"match_all":{}}] } } }
            # Do a bulk-scroll here
            extracted_url_itr = self.article_storage.get_documents(es_query_extracted, bulk_scroll=True)

        # Bad Idea? Create a set-of-extracted-urls for lookup
        logger.info("Going to load all the extracted-urls into memory for lookup")
        start = time.time()
        # Get the URLs from the query results
        self.extracted_url_set = {e_url['_id'] for e_url in extracted_url_itr}
        logger.info("Done. Have {0} urls in lookup index. Time taken:{1} seconds".format(len(self.extracted_url_set), time.time()-start))

    def url_exists(self, url):
        """Check if the given url already exists in the article_storage or not"""
        return (url in self.extracted_url_set)

class ArticleParser():
    def __init__(self, website):
        """The parameter website is used to decide 
        the specific HtmlParserI implementation be used."""
        self.website = website

    def __get_html_parser(self, html_text, url):
        if self.website == Website.KANNADAPRABHA:
            return KannadaPrabhaParser(html_text, url)
        elif self.website == Website.PRAJAVANI:
            return PrajavaniParser(html_text, url)
        # Other parsers go here
        else:
            return None

    def extract_article(self, html_text, url) -> dict:
        """Checks if the page is a valid article page or not.
        If it is valid, extractss the various article fields from the given html_text and 
        returns the final-indexable object.
        Otherwise, returns 'None'"""
        parser = self.__get_html_parser(html_text, url)
        if parser.is_valid_article_page():
            art_text = parser.extract_article_text()
            # If the page has valid article text
            if art_text is not None and len(art_text) > conf_parser.ARTICLE_TEXT_LEN_LIMIT:
                title = parser.extract_title()
                desc = parser.extract_description()
                keywords = parser.extract_keywords()
                pub_date = parser.extract_publish_date()
                # Make the document
                article_doc = make_article_doc(url, title, desc, keywords, pub_date, art_text)
                return article_doc
        
        # In case of failures
        return None

class ArticleExtractor():
    def __init__(self, seed_storage: StorageI, article_storage: StorageI, \
        website: Website, website_base_dir: str, base_url: str, save_batch_limit = 1000):
        """Extract the articles from those URLs from seed_storage whose HTML is already
         downloaded and save the article document to article_storage.

        Args:
            seed_storage (StorageI): Storage containing the seed urls
            article_storage (StorageI): Storage where article doc should be saved
            website (Website): Website name, used to do determine the appropriate parser
            website_base_dir (str): The base path of the downloaded HTML file on the local storage
            base_url (str): The base URL of all the urls
            save_batch_limit (int): Num of article docs to be batched to save in one go
        """
        self.seed_storage = seed_storage
        self.article_storage = article_storage
        self.website_base_dir = website_base_dir
        self.base_url = base_url
        self.save_batch_limit = save_batch_limit

        self.url_lookup = URLLookup(self.article_storage)
        self.article_parser = ArticleParser(website)

    def __get_html_text(self, d_url: str):
        # To avoid confusions
        url_ = d_url.replace("http://", "https://")
        # Remove the base path
        relative_path = url_.replace(self.base_url, '')
        relative_path = relative_path.lstrip("/") # Remove the first '/' in the path, if exists
        html_file_path = os.path.join(self.website_base_dir, relative_path)
        if os.path.isfile(html_file_path):
            # Path exists and it is a file, read the text
            return open(html_file_path, 'rb').read()
        else:
            logger.warning("The html file {0} does not exist for the URL {1}".format(html_file_path, d_url))
            return None

    def __save_article_batch(self, article_batch):
        """Save the list of article documents to article_storage in one go"""
        self.article_storage.save_documents(article_batch)

    def extract_and_save_pending_articles(self):
        """Gather the URLs whose HTML is stored locally and has not been extracted"""
        logger.warning("Going to do a bulk-scroll on the seed storage.")
        
        # URLs whose HTML is stored
        es_query_downloaded = {
            "_source": ["downloaded"],
            "query": {"bool": {"must": [{"term": {"downloaded": "true"} }] } } }
        # Do a bulk-scroll here
        downloaded_url_itr = self.seed_storage.get_documents(es_query_downloaded, bulk_scroll=True)
        downloaded_count = 0
        extracted_count = 0

        # Find the downloaded URLs whose article has not been extracted
        article_batch = []
        for doc in downloaded_url_itr:
            # Get the url from doc
            d_url = doc['_id']
            downloaded_count += 1

            if self.url_lookup.url_exists(d_url):
                # Article is already extracted, Nothing to do here
                continue
            else:
                # Catch any kind of exception here and just log it and move on
                try:
                    logger.debug("Going to extract and index the article from {}".format(d_url))

                    # Get the downloaded HTML text
                    html_text = self.__get_html_text(d_url)
                    if html_text is not None:
                        # Extract the article details
                        article_doc = self.article_parser.extract_article(html_text, d_url)
                        logger.debug('Artile:{}'.format(article_doc))

                        # Accumulate the docs into a mini-batch and save them.
                        # if article_doc is not None, accumulate it
                        if article_doc is not None:
                            article_batch.append(article_doc)
                            extracted_count += 1
                        else:
                            conf_parser.error_logger.error("Empty artilce:{}".format(d_url))

                        if len(article_batch) >= self.save_batch_limit:
                            self.__save_article_batch(article_batch)
                            article_batch = [] # Clear the batch
                    else:
                        # Ignore these errors for now
                        pass

                except:
                    # Just log and move on
                    logger.error("Error on {}".format(d_url))
                    conf_parser.error_logger.error(traceback.format_exc())

        # Save the residual article_doc in the list
        self.__save_article_batch(article_batch)
        logger.info("Done processing. Downloaded urls:{0}. Extracted urls:{1}".format(downloaded_count, extracted_count))

def run_extractor():
    seed_url_config = conf_parser.SYS_CONFIG['url_index']
    article_config = conf_parser.SYS_CONFIG['article_index']
    seed_storage = ESStorage(seed_url_config, read_only=True)
    article_storage = ESStorage(article_config)

    run_config = conf_parser.SYS_CONFIG['run_config']
    website_enum = Website(run_config['website_enum'])
    website_base_dir = run_config['website_base_dir']
    base_url = run_config['base_url']
    art_extractor = ArticleExtractor(seed_storage, article_storage, website_enum, website_base_dir, base_url)
    art_extractor.extract_and_save_pending_articles()

if __name__ == '__main__':
    run_extractor()