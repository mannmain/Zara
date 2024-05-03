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
# PROXY_LIST = """
# zhzEeVuj:SyG1Rnni@166.1.170.244:63262
# zhzEeVuj:SyG1Rnni@166.1.171.159:64590
# zhzEeVuj:SyG1Rnni@166.1.171.169:64590
# zhzEeVuj:SyG1Rnni@166.1.172.137:63460
# """.split('\n')[1:-1]
# PROXY_LIST = """
# FLVSRrbn:rKAcDYVG@85.143.46.138:63672
# FLVSRrbn:rKAcDYVG@85.143.46.142:63672
# FLVSRrbn:rKAcDYVG@85.143.46.145:63672
# FLVSRrbn:rKAcDYVG@85.143.46.148:63672
# """.split('\n')[1:-1]
# W8F7IN:ffoY8O2zgj@45.88.149.72:3000
# W8F7IN:ffoY8O2zgj@185.149.22.39:3000
# W8F7IN:ffoY8O2zgj@185.166.161.184:3000
# W8F7IN:ffoY8O2zgj@185.149.23.97:3000
# PROXY_LIST = """
# zhzEeVuj:SyG1Rnni@166.1.170.244:63262
# zhzEeVuj:SyG1Rnni@166.1.171.159:64590
# zhzEeVuj:SyG1Rnni@166.1.171.169:64590
# zhzEeVuj:SyG1Rnni@166.1.172.137:63460
# FLVSRrbn:rKAcDYVG@85.143.46.138:63672
# FLVSRrbn:rKAcDYVG@85.143.46.142:63672
# FLVSRrbn:rKAcDYVG@85.143.46.145:63672
# FLVSRrbn:rKAcDYVG@85.143.46.148:63672
# W8F7IN:ffoY8O2zgj@45.88.149.72:3000
# W8F7IN:ffoY8O2zgj@185.149.22.39:3000
# W8F7IN:ffoY8O2zgj@185.166.161.184:3000
# W8F7IN:ffoY8O2zgj@185.149.23.97:3000
# """.split('\n')[1:-1]
# PROXY_LIST = """
# W8F7IN:ffoY8O2zgj@188.130.187.245:3000
# W8F7IN:ffoY8O2zgj@46.8.106.199:3000
# W8F7IN:ffoY8O2zgj@5.252.31.147:3000
# W8F7IN:ffoY8O2zgj@31.12.92.82:3000
# """.split('\n')[1:-1]
PROXY_LIST = """
iparchitect_34107_20_04_24:HZaR2ihiBhhNtifAFt@188.143.169.27:30156
""".split('\n')[1:-1]
# -----

PARSE_MAIN_LANGS = [['es', 'en'], ['tr', 'en']]
PARSE_PATH_LANG = [['es', 'es'], ['kz', 'ru'], ['es', 'en'], ['tr', 'en']]
PARSE_NEW_LANGS = [['es', 'es'], ['kz', 'ru']]

# PARSE_MAIN_LANGS = [['es', 'en'], ['kz', 'ru']]
# PARSE_PATH_LANG = [['es', 'es'], ['kz', 'ru'], ['es', 'en']]
# PARSE_NEW_LANGS = [['es', 'es']]
