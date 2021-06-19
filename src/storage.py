import logging
logger = logging.getLogger(__name__)

class StorageI:
    def write_line(self, line):
        pass
    def close(self):
        pass

class FileStorage(StorageI):
    def __init__(self, file_path):
        self.file_out = open(file_path, "a+")
        logger.warning('Going to write/append the results to {} file.'.format(file_path))
    
    def write_line(self, line):
        """Write/append a line to file"""
        line_to_write = line + '\n'
        self.file_out.write(line_to_write)
        logger.debug('Saved:', line)

    def close(self):
        self.file_out.flush()
        self.file_out.close()

