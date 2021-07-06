from storage import StorageI
from es_helper import ESHelper

import logging
logger = logging.getLogger(__name__)

# Change the default logging level of Elasticsearch as well
es_logger = logging.getLogger('elasticsearch')
es_logger.setLevel(logging.WARNING)

class ESStorage(StorageI):
    def __init__(self, es_index_conf, read_only=False):
        self.eshelper = ESHelper(es_index_conf)
        self.read_only = read_only
        logger.warning('Connected to {0} index. Read only:{1}'\
            .format(self.eshelper.get_index_name(), self.read_only))
    
    def __check_writeability(self):
        """Exit if the index is not write-able"""
        if self.read_only:
            logger.error('Cannot write to index {}. Opened in read-only mode!'\
                .format(self.eshelper.get_index_name(), self.read_only))
            exit()

    def storage_exists(self):
        if self.eshelper.index_exists():
            return True
        return False

    def save_doc(self, doc, update_if_exists=False):
        """Index the doc"""
        self.__check_writeability()
        return self.eshelper.index_doc(doc, update_if_exists)

    def save_documents(self, documents, update_if_exists=False):
        """Index multile documents"""
        self.__check_writeability()
        self.eshelper.index_documents(documents, update_if_exists)

    def get_doc_by_id(self, id):
        """Get a document by id"""
        return self.eshelper.doc_by_id(id)

    def get_documents(self, query, bulk_scroll=False):
        """Get the documents for the given query.
        Set bulk_scroll=True if you intend to consume the documents of the entire index!
        """
        if bulk_scroll:
            return self.eshelper.bulk_scroll(query)
        else:
            return self.eshelper.search(query)

    def close(self):
        self.eshelper.close()