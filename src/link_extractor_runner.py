import glob
import os
import logging
logger = logging.getLogger(__name__)

from link_extractor import LinkExtractor
from es_doc_maker import make_html_path_doc
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
    html_path_store: StorageI, filter_domains=[]):
    """ Fetch all the HTML pages under website_base_dir recursively,
    Extract and clean all the URLs from those HTML pages,
    Filter the URLs with matching domain strings in filter_domains,
    Save those links to a storage """

    logger.info("####{}####".format(run_name))

    all_html_paths = get_all_html_file_paths(website_base_dir)
    for html_file_path in all_html_paths:
        logger.debug('-'*20)
        logger.debug(html_file_path)
        # Get the relative path of the HTML file and save
        relative_path = html_file_path.replace(website_base_dir, '')
        # Prepare the doc to be saved
        doc = make_html_path_doc(relative_path)
        html_path_store.save_doc(doc)
        
        # Extract links
        html_file = open(html_file_path, 'r')
        html_text = html_file.read()
        links = extractor.extract(html_text, base_url, filter_domains)
        extractor.save_links(links)
    
    logger.info("Completed {}".format(run_name))

if __name__ == '__main__':
    logger.basicConfig(level=logging.WARN, format='%(asctime)s :: %(levelname)s :: %(message)s')

    ##TEST case 
    # test()

    # Full run
    # Name this run
    run_name = 'run1'
    base_url = 'https://www.kannadaprabha.com/'
    filter_domains = ['kannadaprabha']
    website_base_dir = '/home/adiga/my_work/kannada-news-dataset/crawling/snapshot_download/kannadaprabha/run1/websites/www.kannadaprabha.com/'

    # #The old-school file storage
    # output_base_dir = '/home/adiga/my_work/kannada-news-dataset/crawling/sample_output/'
    # output_run_dir = os.path.join(output_base_dir, run_name)
    # if not os.path.exists(output_run_dir):
    #     os.makedirs(output_run_dir)
    # fs = FileStorage(os.path.join(output_run_dir, 'extracted_links.txt'))
    # html_path_fs = FileStorage(os.path.join(output_run_dir, 'html_file_paths.txt'))

    # Load the ElasticSearch storage indices
    extracted_url_storage = ESStorage(conf_parser.SYS_CONFIG['extracted_url_index'])
    existing_url_storage = ESStorage(conf_parser.SYS_CONFIG['existing_html_path_index'])

    extractor = LinkExtractor(extracted_url_storage)
    
    run_full(run_name, base_url, website_base_dir, extractor, existing_url_storage, filter_domains)