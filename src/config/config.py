import os
from dotenv import load_dotenv

load_dotenv()

# FTP
FTP_HOST_TR = os.getenv('FTP_HOST_TR')
FTP_USER_TR = os.getenv('FTP_USER_TR')
FTP_PASSWORD_TR = os.getenv('FTP_PASSWORD_TR')

FTP_HOST_ES = os.getenv('FTP_HOST_ES')
FTP_USER_ES = os.getenv('FTP_USER_ES')
FTP_PASSWORD_ES = os.getenv('FTP_PASSWORD_ES')
# -----

# TG
TG_API_TOKEN = os.getenv('TG_API_TOKEN')
TG_GROUP_ID = os.getenv('TG_GROUP_ID')
TG_NAME_PARSE = os.getenv('TG_NAME_PARSE')
# -----

# MONGODB
MONGODB_URL = os.getenv('MONGODB_URL')
NAME_DB = os.getenv('NAME_DB')
NAME_COLLECTION = os.getenv('NAME_COLLECTION')
# -----

STEP_LEN_UPLOAD = int(os.getenv('STEP_LEN_UPLOAD'))
TIME_TO_START = os.getenv('TIME_TO_START')

# PROXY
PROXY = os.getenv('PROXY')
# -----

PARSE_MAIN_LANGS = [['es', 'en'], ['tr', 'en']]
PARSE_PATH_LANG = [['es', 'es'], ['kz', 'ru'], ['es', 'en'], ['tr', 'en']]
PARSE_NEW_LANGS = [['es', 'es'], ['kz', 'ru']]

# PARSE_MAIN_LANGS = [['es', 'en'], ['kz', 'ru']]
# PARSE_PATH_LANG = [['es', 'es'], ['kz', 'ru'], ['es', 'en']]
# PARSE_NEW_LANGS = [['es', 'es']]
