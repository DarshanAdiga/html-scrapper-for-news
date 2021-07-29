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

elastic_conf = conf_parser.SYS_CONFIG['article_index']
es_article_storage = ESStorage(elastic_conf, read_only=True)

es_query_text_len = {
    "_source": ["url", "description", "text_len"],
    "query":{"bool":{"must":[{"range":{"text_len":{"gt":"-1","lt":"200"}}}]}}
}

# Do a bulk-scroll here
result_itr = es_article_storage.get_documents(es_query_text_len, bulk_scroll=True)
    

