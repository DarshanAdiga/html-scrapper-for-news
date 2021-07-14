from es_storage import ESStorage
from file_storage import FileStorage
from storage import StorageI
import conf_parser
import json

import logging
logger = logging.getLogger(__name__)

class IndexDumper():
    def __init__(self, index_storage: StorageI, target_storage: StorageI, json_query: dict):
        self.index_storage = index_storage
        self.target_storage = target_storage
        self.json_query = json_query
        logger.info("Source: {}".format(str(self.index_storage)))
        logger.info("Target: {}".format(str(self.target_storage)))
        logger.warning("Dump Query: {}".format(self.json_query))

    def fetch_and_save_dump(self):
        res_itr = self.index_storage.get_documents(self.json_query, bulk_scroll=True)
        cnt=0
        for doc in res_itr:
            doc = doc["_source"]
            doc = json.dumps(doc)
            self.target_storage.save_doc(doc)
            cnt += 1
        logger.warning("Fetched and saved {} docs".format(cnt))

    def close(self):
        self.index_storage.close()
        self.target_storage.close()

def runner(dump_json_query=None):
    # The default json query
    if dump_json_query is None:
        dump_json_query = {
            "_source": [
                "url", "title",
                "description", "keywords",
                "publish_date", "article_text",
                "text_len"],
            "query":{"bool":{"must":[{"range":{"text_len":{"gt":"20"}}}]}}
        }

    # Source index
    article_index_conf = conf_parser.SYS_CONFIG['article_index']
    source_index = ESStorage(article_index_conf, read_only=True)

    # Target storage
    index_dump_conf = conf_parser.SYS_CONFIG['index_dump_conf']
    dump_file_path = index_dump_conf['dump_file_path']
    file_storage = FileStorage(dump_file_path)

    # Fetch and save
    index_dumper = IndexDumper(source_index, file_storage, dump_json_query)
    index_dumper.fetch_and_save_dump()
    index_dumper.close()


if __name__ == "__main__":
    runner()