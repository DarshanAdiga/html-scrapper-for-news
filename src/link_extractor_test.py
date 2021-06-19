from link_extractor import LinkExtractor

# Load a sample HTML file
base_url = 'https://www.kannadaprabha.com/'
html_file = '/home/adiga/my_work/kannada-news-dataset/crawling/snapshot_download/kannadaprabha/run1/websites/www.kannadaprabha.com/index.html'
f = open(html_file, 'r')
html_text = f.read()

le = LinkExtractor()
links = le.extract(html_text, base_url)
for lnk in links:
    print(lnk)