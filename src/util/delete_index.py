# Code to fix the importing of submodules
from pathlib import Path
import sys
if __package__ is None:                  
    DIR = Path(__file__).resolve().parent
    sys.path.insert(0, str(DIR.parent))
    __package__ = DIR.name


import conf_parser
from es_helper import ESHelper
import time

elastic_conf = conf_parser.SYS_CONFIG['url_index']
esh = ESHelper(elastic_conf)

print('GOING TO DELETE {}'.format(esh.get_index_name()))
print('ARE YOU SURE ABOUT THIS??')
time.sleep(5)
esh.delete_index()