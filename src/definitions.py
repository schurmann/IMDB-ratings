from os import path
from collections import OrderedDict
from configparser import ConfigParser

ROOT_DIR = path.normpath(path.join(path.dirname(path.abspath(__file__)), '../'))
CFG = ConfigParser()
CFG.read(f'{ROOT_DIR}/env.ini')
DB_CONF = CFG['DATABASE']
USERS = OrderedDict(CFG['USERS'])
