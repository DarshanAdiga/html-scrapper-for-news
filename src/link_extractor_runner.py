import glob
import os
from urllib.parse import urljoin
import logging
logger = logging.getLogger(__name__)

from link_extractor import LinkExtractor
from es_doc_maker import make_url_doc
from storage import StorageI
import conf_parser
from es_storage import ESStorage

def test():
    # Load a sample HTML file
    base_url = 'https://www.kannadaprabha.com/'
    html_file = '/home/adiga/my_work/kannada-news-dataset/crawling/snapshot_download/kannadaprabha/run1/websites/www.kannadaprabha.com/index.html'
    f = open(html_file, 'r')
    html_text = f.read()

    le = LinkExtractor()
    links = le.extract(html_text, base_url)
    for lnk in links:
        logger.info(lnk)

def get_all_html_file_paths(website_base_dir):
    return list(glob.glob(website_base_dir+'/**/*.html',recursive = True))

def run_full(run_name, base_url, website_base_dir, extractor: LinkExtractor, \
    url_storage: StorageI, filter_domains=[]):
    """ Fetch all the HTML pages under website_base_dir recursively,
    Extract and clean all the URLs from those HTML pages,
    Filter the URLs with matching domain strings in filter_domains,
    Save those links to a storage """

    logger.info("####{}####".format(run_name))

    all_html_paths = get_all_html_file_paths(website_base_dir)
    for html_file_path in all_html_paths:
        logger.debug('-'*20)
        logger.debug(html_file_path)

        # Get the relative path of the HTML file and convert it into a valid URL
        relative_path = html_file_path.replace(website_base_dir, '')
        html_url = urljoin(base_url, relative_path)

        # if html_file_path is a directory, then simply save it as a undownloaded-HTML url
        if os.path.isdir(html_file_path):
            # Prepare and save the URL doc
            doc = make_url_doc(html_url, downloaded=False)
            url_storage.save_doc(doc)
        else:    
            # Prepare and save the URL doc
            doc = make_url_doc(html_url, downloaded=True)
            url_storage.save_doc(doc)
            
            # Extract links
            html_file = open(html_file_path, 'rb')
            html_text = html_file.read()
            links = extractor.extract(html_text, base_url, filter_domains)
            extractor.save_links(links)
    
    logger.info("Completed {}".format(run_name))

if __name__ == '__main__':
    ##TEST case 
    # test()

    # Full run
    # Load the config
    run_config = conf_parser.SYS_CONFIG['run_config']

    # Name this run
    run_name = run_config['run_name']
    base_url = run_config['base_url']
    website_base_dir = run_config['website_base_dir']
    filter_domains = run_config['filter_domains']

    # The ElasticSearch storage indices
    url_storage = ESStorage(conf_parser.SYS_CONFIG['url_index'])
    extractor = LinkExtractor(url_storage)
    # Start the full run
    run_full(run_name, base_url, website_base_dir, extractor, url_storage, filter_domains)