from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
logger = logging.getLogger(__name__)
    
from es_doc_maker import make_url_doc
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
                
    def extract(self, html_text, base_url, filter_domains=[]):
        """Extract all the possible links from the given html text
        and return a set of unique links. If filter_domain is given, only those URLs 
        which has any of the filter_domains string in their domain will be returned"""
        html_doc = BeautifulSoup(html_text, "html.parser")
        # Extract links from anchors
        links = self.__extract_from_anchors(html_doc)
        # TODO Extract links from other tags here
        
        # Convert if required
        links = self.__to_absolute_links(links, base_url)

        # Filter out only the URLs from the required domain
        links = self.__filter_links(links, filter_domains)

        return links

    def save_links(self, links):
        """Saves the links to the pre-configured storage"""

        if not self.storage:
            logger.error('No Storage object defined!')
            exit(1)
        
        # Prepare a doc to be saved
        documents = [make_url_doc(ln, downloaded=False) for ln in links]
        # Save
        self.storage.save_documents(documents)
        logger.info('Stored {} links successfully'.format(len(links)))

    def __filter_links(self, links, filter_domains):
        """Return only those URLs haivng matching filter_domains strings"""
        filtered_links = set()
        # Very bad code ahead! If you have time, fix it!
        for ln in links:
            ln_parsed = urlparse(ln)
            for dom in filter_domains:
                if dom in str(ln_parsed.hostname):
                    filtered_links.add(ln)
                    break # out of inner most loop

        return filtered_links

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

        