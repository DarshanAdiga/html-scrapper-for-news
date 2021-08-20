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
es_seed_storage = ESStorage(elastic_conf, read_only=True)

es_seed_storage.eshelper.index_doc({"id": "url", "url": "", "title": "", "description": "", "keywords": "", "publish_date": "", "article_text": "", "text_len": 0})
ind = es_seed_storage.eshelper.index
dt = es_seed_storage.eshelper.doc_type

from elasticsearch.client import IndicesClient
iclient = IndicesClient(es_seed_storage.eshelper.es)
#put_mapping
res = iclient.put_mapping({"date_detection": False}, index=ind)
print(res)
es_seed_storage.eshelper.es.delete(index=ind, doc_type=dt, id="url")
