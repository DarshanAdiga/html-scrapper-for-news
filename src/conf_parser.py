import yaml
SYS_CONFIG=yaml.load(open('config/sys_config.yml', 'r'))

# Configure logging
import logging
log_config = SYS_CONFIG['log_config']
logging.basicConfig(level=log_config['level'], format='%(asctime)s :: %(levelname)s :: %(message)s')