import elasticsearch
from elasticsearch import Elasticsearch
import json
import conf_parser
import traceback

import logging
logger = logging.getLogger(__name__)

class ESHelper():
    def __init__(self, elastic_conf):
        # Initialize the connection
        self.elastic_conf = elastic_conf
        self.es = self.__init_es()
        self.index = elastic_conf['index']
        self.doc_type = elastic_conf['doc_type']

    def get_index_name(self):
        return self.index
        
    def __init_es(self):
        """
        Initializes the elastic-search client and returns it
        """
        es = Elasticsearch([{'host': self.elastic_conf['host'], 'port': self.elastic_conf['port']}])
        logger.info('Connected to Elastic Search:' + str(es.ping()))
        return es

    def index_doc(self, doc):
        # Use doc specific id while indexing to avoid duplication
        self.es.index(index=self.index, doc_type=self.doc_type, id=doc['id'], body=doc)

    def index_documents(self, documents):
        """
        Indexes the given list of documents onto the configured index
        """
        drop_count = 0
        for doc in documents:
            try:
                self.index_doc(doc)
            except KeyError:
                drop_count += 1
                traceback.print_exc()
            except elasticsearch.exceptions.RequestError:
                drop_count += 1
                traceback.print_exc()

        logger.info('Indexed {0} Dropped {1}'.format(len(documents)-drop_count, drop_count))
        logger.info('Current index size {0}'.format(self.get_index_size()))

    def get_index_size(self):
        """
        Return the total number of docs present in the index
        """
        return self.es.indices.stats()['indices'][self.index]['total']['docs']['count']

    def doc_by_id(self, id):
        """
        Get the doc with the given id
        """
        return self.es.get(index=self.index, doc_type=self.doc_type, id=id)

    def search(self, json_query):
        """
        Search the index using given json_query and return the list of article objects
        """
        res = self.es.search(index=self.index, body=json_query)
        #print(json.dumps(res, indent=2))
        # Process the results and return the documents only
        documents = [src['_source'] for src in res['hits']['hits']]
        return documents

    def delete_index(self):
        """Deletes the given index! Use with caution!"""
        logger.warning("Going to DELETE the index {0} permanently!".format(self.index))
        self.es.indices.delete(index=self.index)
        logger.info("Deleted {}".format(self.index))


if __name__ == "__main__":    
    # Testing
    elastic_conf = conf_parser.SYS_CONFIG['elastic_test']
    esh = ESHelper(elastic_conf)
    esh.index_documents([{'id': '123', 'url': 'https://test.com'}])

    # For cleaning the ES
    #esh.delete_index()
    