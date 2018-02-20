import os
from configparser import ConfigParser

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CFG = ConfigParser()
CFG.read(f'{ROOT_DIR}/env.ini')
DB_CONF = CFG['DATABASE']
USERS = CFG['USERS']
