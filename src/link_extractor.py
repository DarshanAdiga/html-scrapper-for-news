from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

logger = logging.getLogger(__name__)
    
from storage import StorageI

class LinkExtractor:
    def __init__(self, storage: StorageI=None):
        self.storage = storage
    
    def __extract_from_anchors(self, html_doc):
        link_set = set()
        for anc in html_doc.find_all('a'):
            if 'href' in anc.attrs:
                link_set.add(anc.attrs['href'])
        return link_set
                
    def extract(self, html_text, base_url):
        """Extract all the possible links from the given html text
        and return a set of unique links"""
        html_doc = BeautifulSoup(html_text, "html.parser")
        # Extract links from anchors
        links = self.__extract_from_anchors(html_doc)
        # TODO Extract links from other tags here
        
        # Convert if required
        links = self.__to_absolute_links(links, base_url)
        return links

    def extract_save(self, html_text, base_url):
        """Extracts the links using 'extract()' method and saves those links
        to the storage"""

        if not self.storage:
            logger.error('No Storage object defined!')
            exit(1)
        
        # Extract the links
        links = self.extract(html_text, base_url)
        
        # Then save the links
        for ln in links:
            self.storage.write_line(ln)
        logger.info('Stored {} links successfully'.format(len(links)))

    def __to_absolute_links(self, links, base_url):
        """Convert the relative links, if any, in the given list of links,
         to absolute and valid links and return the list"""
        abs_link_set = set()
        for ln in links:
            if not str(ln).startswith("http"):
                logger.debug('Relative link found:: {}'.format(ln))
                # Convert relative to absolute
                new_url = urljoin(base_url, ln)
            else:
                new_url = ln
            # Copy to another set
            abs_link_set.add(new_url)

        return abs_link_set

        