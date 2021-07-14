from storage import StorageI

import logging
logger = logging.getLogger(__name__)

class FileStorage(StorageI):
    def __init__(self, file_path):
        self.file_out = open(file_path, "w+")
        logger.warning('Going to write/append the results to {} file.'.format(file_path))
    
    def save_doc(self, doc: str):
        """Write/append a doc to file"""
        line_to_write = doc + '\n'
        self.file_out.write(line_to_write)
        logger.debug('Saved:', doc)

    def save_documents(self, documents):
        for doc in documents:
            self.save_doc(doc)
            
    def close(self):
        self.file_out.flush()
        self.file_out.close()

