import elasticsearch
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from elasticsearch.client import IndicesClient
from elasticsearch.exceptions import ConflictError
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
        self.doc_type = self.index # use the index name itself

    def get_index_name(self):
        return self.index
        
    def __init_es(self):
        """
        Initializes the elastic-search client and returns it
        """
        es = Elasticsearch([{'host': self.elastic_conf['host'], 'port': self.elastic_conf['port']}])
        logger.info('Connected to Elastic Search:' + str(es.ping()))
        return es

    def index_exists(self):
        """Check if index exists or not"""
        return IndicesClient(self.es).exists(self.index)

    def index_doc(self, doc, update_if_exists=False):
        if update_if_exists:
            OP_TYPE = "index" # Create or update
        else:
            OP_TYPE = "create" # Create only if absent

        try:
            # Use doc specific id while indexing to avoid duplication
            return self.es.index(index=self.index, doc_type=self.doc_type, id=doc['id'], body=doc, op_type=OP_TYPE)
        except ConflictError as c_error:
            conf_parser.error_logger.error("Indexing failed! Duplicate document: {}".format(doc))
        
        return None

    def index_documents(self, documents, update_if_exists=False):
        """
        Indexes the given list of documents onto the configured index
        """
        drop_count = 0
        for doc in documents:
            try:
                resp_doc = self.index_doc(doc, update_if_exists=update_if_exists)
                if resp_doc is None:
                    drop_count += 1
            except KeyError:
                drop_count += 1
                traceback.print_exc()
            except elasticsearch.exceptions.RequestError:
                drop_count += 1
                traceback.print_exc()

        logger.warning('## Indexed {0} Dropped {1}'.format(len(documents)-drop_count, drop_count))
        logger.info('Current index size {0}'.format(self.get_index_size()))

    def get_index_size(self):
        """
        Return the total number of docs present in the index
        """
        if self.index_exists():
            return self.es.indices.stats()['indices'][self.index]['total']['docs']['count']
        else:
            return 0

    def doc_by_id(self, id):
        """
        Get the doc with the given id
        """
        return self.es.get(index=self.index, doc_type=self.doc_type, id=id)

    def search(self, json_query):
        """
        Search the index using given json_query and return the list of article objects
        """
        res = self.es.search(index=self.index, doc_type=self.doc_type, body=json_query)
        #print(json.dumps(res, indent=2))
        # Process the results and return the documents only
        documents = [src['_source'] for src in res['hits']['hits']]
        return documents

    def bulk_scroll(self, json_query):
        """Fetch all the documents from the index using a scroll option.
        Returns an iterator which gives out all the documents! Becareful about this guy!"""
        # TODO Wait for 15 mins max before cleaning the scroll
        result_itr = scan(self.es, index=self.index, doc_type=self.doc_type, query=json_query, scroll='15m', size=1000)
        return result_itr

    def delete_index(self):
        """Deletes the given index! Use with caution!"""
        logger.warning("Going to DELETE the index {0} permanently!".format(self.index))
        self.es.indices.delete(index=self.index)
        logger.info("Deleted {}".format(self.index))

    def close(self):
        self.es.close()


if __name__ == "__main__":    
    # Testing
    elastic_conf = conf_parser.SYS_CONFIG['elastic_test']
    esh = ESHelper(elastic_conf)
    
    print('Index Exists:', esh.index_exists())
    #esh.index_documents([{'id': '123', 'url': 'https://test.com'}])

    # print('>>', esh.index_doc({'key':1, 'id': 123}, update_if_exists=True))
    # print('>>', esh.index_doc({'key':1, 'id': 123}, update_if_exists=True))
    # print('>>', esh.index_doc({'key':1, 'id': 234}, update_if_exists=True))
    # print('>>', esh.index_doc({'key':2, 'id': 123}, update_if_exists=True))

    # esh.index_documents([{'key':1, 'id': 123}, {'key':1, 'id': 123}, {'key':1, 'id': 234}])
    
    # q_body={"_source": ["downloaded"],
    #         "query": {"bool": {"must": [{"term": {"downloaded": "true"} }] } } }
    
    # res_itr = esh.bulk_scroll(q_body)
    # cnt=0
    # for ri in res_itr:
    #     cnt += 1
    #     if cnt > 1000:
    #         print('More than 1k')
    #         break
    #     print(ri)

    # For cleaning the ES
    # esh.delete_index()

    # Close the connection
    esh.close()
    