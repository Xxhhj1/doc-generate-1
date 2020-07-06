import os

from sekg.mysql.factory import MysqlSessionFactory

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
# the output dir
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')
LABEL_DATA_DIR = os.path.join(ROOT_DIR, 'label_data')
# the data dir
DATA_DIR = os.path.join(ROOT_DIR, 'data')
Log_DIR = os.path.join(ROOT_DIR, 'logs')
NEO4j_CONFIG_PATH = os.path.join(ROOT_DIR, 'neo4j_config.json')
