from storage import StorageI
from es_helper import ESHelper

import logging
logger = logging.getLogger(__name__)

class ESStorage(StorageI):
    def __init__(self, es_index_conf):
        self.eshelper = ESHelper(es_index_conf)
        logger.warning('Going to index the docs to {} index.'.format(self.eshelper.get_index_name()))
    
    def save_doc(self, doc):
        """Index the doc"""
        self.eshelper.index_doc(doc)

    def save_documents(self, documents):
        """Index multile documents"""
        self.eshelper.index_documents(documents)

    def close(self):
        pass