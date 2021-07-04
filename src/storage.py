import logging
logger = logging.getLogger(__name__)

class StorageI:
    def storage_exists(self):
        pass
    
    def save_doc(self, doc):
        pass

    def save_documents(self, documents):
        pass
    
    def get_doc_by_id(self, id):
        pass

    def get_documents(self, query, bulk_scroll=False):
        pass
    
    def close(self):
        pass
