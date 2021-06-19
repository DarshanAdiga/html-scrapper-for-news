from bs4 import BeautifulSoup
from urllib.parse import urljoin

class FileStorage:
    def __init__(self):
        pass
    
    def write_line(self, line):
        # TODO
        print('Write:', line)
    
class LinkExtractor:
    def __init__(self, storage: FileStorage=None):
        pass
    
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

    def __to_absolute_links(self, links, base_url):
        """Convert the relative links, if any, in the given list of links,
         to absolute and valid links and return the list"""
        abs_link_set = set()
        for ln in links:
            if not str(ln).startswith("http"):
                #print('Warn:Relative link found:: {}'.format(ln))
                # Convert relative to absolute
                new_url = urljoin(base_url, ln)
            else:
                new_url = ln
            # Copy to another set
            abs_link_set.add(new_url)

        return abs_link_set

        