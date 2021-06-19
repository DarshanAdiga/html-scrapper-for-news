import glob

from link_extractor import LinkExtractor
from storage import FileStorage
import logging
logger = logging.getLogger(__name__)

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

def run_full(run_name, base_url, website_base_dir, extractor: LinkExtractor):
    """ Fetch all the HTML pages under website_base_dir recursively,
    Extract and clean all the URLs from those HTML pages,
    Save those links to a storage """

    logger.info("####{}####".format(run_name))

    all_html_paths = get_all_html_file_paths(website_base_dir)
    for html_file_path in all_html_paths:
        logger.debug('-'*20)
        logger.debug(html_file_path)
        html_file = open(html_file_path, 'r')
        html_text = html_file.read()
        extractor.extract_save(html_text, base_url)
    
    logger.info("Completed {}".format(run_name))

if __name__ == '__main__':
    ##TEST case 
    # test()

    # Full run
    # Name this run
    run_name = "run2"
    base_url = 'https://www.kannadaprabha.com/'
    website_base_dir = '/home/adiga/my_work/kannada-news-dataset/crawling/snapshot_download/kannadaprabha/run1/websites/www.kannadaprabha.com/'

    output_storage_dir = '/home/adiga/my_work/kannada-news-dataset/crawling/sample_output/'
    fs = FileStorage(output_storage_dir + 'extracted_links.txt')
    extractor = LinkExtractor(fs)
    run_full(run_name, base_url, website_base_dir, extractor)