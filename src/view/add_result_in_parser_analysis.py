import time

import requests
from datetime import datetime

from config.config import TG_NAME_PARSE
from tg.notification import send_msg

FORMAT_TIME = '%Y-%m-%dT%H:%M:%S'
secret_key = 'UEYG7823T*6*WJKEHGBbwgDFLKBMKLQ!@LMWEHJBCDDV'
host = '32d209d78239.vps.myjino.ru'


def load_res_to_parser_analysis(data_finally):
    json_data = {
        'parser_name': f'{TG_NAME_PARSE}_{data_finally["currency"]}',
        'count_cards': data_finally['card'],
        'count_active_cards': data_finally['card_active'],
        'count_variants': data_finally['vars'],
        'count_active_variants': data_finally['vars_active'],
        'datetime': datetime.utcnow().strftime(FORMAT_TIME)
    }
    for _ in range(10):
        try:
            response = requests.post(f'http://{host}/result/create?secret_key={secret_key}', json=json_data)
            response_json = response.json()
            if response_json['status'] == 'Ok':
                return True
            else:
                msg = f'{TG_NAME_PARSE}\n{datetime.now().strftime("%m.%d %H:%M")}\n[Status error НА PARSER_ANALYSIS]\nresponse_json: {response_json}'
                send_msg(msg, parser_analysis=True)
        except Exception as ex:
            msg = f'{TG_NAME_PARSE}\n{datetime.now().strftime("%m.%d %H:%M")}\n[ОШИБКА НА PARSER_ANALYSIS]\nex: {ex}'
            send_msg(msg, parser_analysis=True)
        time.sleep(10)
