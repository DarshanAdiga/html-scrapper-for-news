import yaml

# For testing
# SYS_CONFIG=yaml.load(open('config/test_sys_config.yml', 'r'))

# Actual run
# SYS_CONFIG=yaml.load(open('config/kannadaprabha_sys_config.yml', 'r'))
# SYS_CONFIG=yaml.load(open('config/prajavani_sys_config.yml', 'r'))
SYS_CONFIG=yaml.load(open('config/vijayakarnataka_sys_config.yml', 'r'))

#------------------------------
# Other configurations

# Min length of the article text, to be considered as valid
ARTICLE_TEXT_LEN_LIMIT = 100
#------------------------------


# Configure logging
import logging
log_config = SYS_CONFIG['log_config']
LOG_FORMAT = '%(asctime)s:%(name)s:%(levelname)s: %(message)s'
logging.basicConfig(level=log_config['level'], format=LOG_FORMAT)

# Configure the error logger
error_logger = logging.getLogger('ERROR_LOGGER')
LOG_FILE_ERROR = log_config['error_log_file']
file_handler_error = logging.FileHandler(LOG_FILE_ERROR, mode='w')
file_handler_error.setFormatter(logging.Formatter(LOG_FORMAT))
file_handler_error.setLevel(logging.ERROR)
error_logger.addHandler(file_handler_error)