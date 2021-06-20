import glob
import os
import logging
logger = logging.getLogger(__name__)

from link_extractor import LinkExtractor
from storage import FileStorage, StorageI

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
    html_path_fs: StorageI, filter_domains=[]):
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
        html_path_fs.write_line(relative_path)
        
        # Extract links
        html_file = open(html_file_path, 'r')
        html_text = html_file.read()
        links = extractor.extract(html_text, base_url, filter_domains)
        extractor.save_links(links)
    
    logger.info("Completed {}".format(run_name))

if __name__ == '__main__':
    ##TEST case 
    # test()

    # Full run
    # Name this run
    run_name = 'run1'
    base_url = 'https://www.kannadaprabha.com/'
    filter_domains = ['kannadaprabha']
    website_base_dir = '/home/adiga/my_work/kannada-news-dataset/crawling/snapshot_download/kannadaprabha/run1/websites/www.kannadaprabha.com/'

    output_base_dir = '/home/adiga/my_work/kannada-news-dataset/crawling/sample_output/'
    output_run_dir = os.path.join(output_base_dir, run_name)
    if not os.path.exists(output_run_dir):
        os.makedirs(output_run_dir)

    fs = FileStorage(os.path.join(output_run_dir, 'extracted_links.txt'))
    extractor = LinkExtractor(fs)
    html_path_fs = FileStorage(os.path.join(output_run_dir, 'html_file_paths.txt'))
    run_full(run_name, base_url, website_base_dir, extractor, html_path_fs, filter_domains)