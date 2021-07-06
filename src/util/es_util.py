# Code to fix the importing of submodules
from pathlib import Path
import sys
import json
if __package__ is None:                  
    DIR = Path(__file__).resolve().parent
    sys.path.insert(0, str(DIR.parent))
    __package__ = DIR.name


import conf_parser
from es_storage import ESStorage
import time

elastic_conf = conf_parser.SYS_CONFIG['url_index']
es_seed_storage = ESStorage(elastic_conf, read_only=True)

##> Count the URLs whose HTML has already been downloaded
#----------------------
es_query_downloaded = {
    "_source": ["downloaded"],
    "query": {"bool": {"must": [{"term": {"downloaded": "true"} }] } } }
# Do a bulk-scroll here
downloaded_url_itr = es_seed_storage.get_documents(es_query_downloaded, bulk_scroll=True)
downloaded_count = 0

# Save the results to a temp file
write_file = open('logs/dump.jl', 'w')
for doc in downloaded_url_itr:
    downloaded_count += 1
    write_file.write(json.dumps(doc) + '\n')

es_seed_storage.close()
print("Count of docs with 'downloaded'=True: {}".format(downloaded_count))