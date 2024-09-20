import json
import time
from datetime import datetime

import requests

from config.config import TG_GROUP_ID, TG_API_TOKEN, TG_NAME_PARSE, TG_GROUP_ID_PARSER_ANALYSIS, \
    TG_API_TOKEN_PARSER_ANALYSIS


def send_file(path):
    params = {
        'chat_id': TG_GROUP_ID,
        'disable_notification': False,
    }
    files = {
        'document': open(f'{path}', 'rb'),
    }
    while True:
        try:
            response = requests.post(f'https://api.telegram.org/bot{TG_API_TOKEN}/sendDocument', files=files, params=params)
            if response.status_code == 200:
                break
            else:
                try:
                    print(f'ERROR SEND MSG status {response.status_code}) - {response.text}')
                except:
                    print(f'ERROR SEND MSG status {response.status_code})')
        except Exception as ex:
            print(f"ERROR SEND MSG - {ex}")


def send_msg(msg, parser_analysis=False):
    if parser_analysis:
        group_id = TG_GROUP_ID_PARSER_ANALYSIS
        api_token = TG_API_TOKEN_PARSER_ANALYSIS
    else:
        group_id = TG_GROUP_ID
        api_token = TG_API_TOKEN
    json_data = {
        'chat_id': group_id,
        'text': msg,
        'disable_notification': False,
    }
    while True:
        try:
            response = requests.post(f'https://api.telegram.org/bot{api_token}/sendMessage', json=json_data)
            if response.status_code == 200:
                break
            else:
                try:
                    print(f'ERROR SEND MSG status {response.status_code}) - {response.text}')
                except:
                    print(f'ERROR SEND MSG status {response.status_code})')
        except Exception as ex:
            print(f"ERROR SEND MSG - {ex}")
            time.sleep(10)


def start_and_send_msg(msg=''):
    msg += f'{TG_NAME_PARSE}\n{datetime.now().strftime("%m.%d %H:%M")}\n[ПАРСЕР ЗАПУЩЕН]\n'
    send_msg(msg)


def end_and_send_msg(msg=''):
    msg += f'{TG_NAME_PARSE}\n{datetime.now().strftime("%m.%d %H:%M")}\n[ПАРСЕР ЗАКОНЧИЛ РАБОТУ]\n'
    send_msg(msg)


def finally_info_and_send_msg(data, msg=''):
    msg += f'{TG_NAME_PARSE}\n{datetime.now().strftime("%m.%d %H:%M")}\n[ВЫГРУЖЕНО]\n'
    msg += f'Карточек: {data["card"]} (Активных: {data["card_active"]})\nВариаций: {data["vars"]} (Активных: {data["vars_active"]})'
    send_msg(msg)


def error_and_send_msg(error, article, msg=''):
    msg += f'{TG_NAME_PARSE}\n{datetime.now().strftime("%m.%d %H:%M")}\n[ОШИБКА]\nArticle: {article}\nТекст ошибки: {error}'
    send_msg(msg)


def msg_to_del_item(reason, article, msg=''):
    msg += f'{TG_NAME_PARSE}\n{datetime.now().strftime("%m.%d %H:%M")}\n[Удалить предмет]\nАртикул {article} {reason}'
    send_msg(msg)
    with open('files/delete_items.json', 'r', encoding='UTF-8') as file:
        data = json.load(file)
    data.append([article, reason])
    with open('files/delete_items.json', 'w', encoding='UTF-8') as file:
        json.dump(data, file)


def get_info_and_send_msg(msg='', send_msg_flag=True):
    data = {}
    msg += f'{TG_NAME_PARSE}\n{datetime.now().strftime("%m.%d %H:%M")}\n[ВЫГРУЖЕНО]\n'
    try:
        with open('ftp/json.json', 'r', encoding='UTF-8') as file:
            json_file = json.load(file)
        count_var = 0
        for i in json_file:
            if 'variations' in i.keys():
                count_var += len(i['variations'])

        len_available_card = 0
        len_available_var = 0
        for i in json_file:
            flag = False
            for j in i['variations']:
                if j['price'] == 0 or j['quantity'] == 0:
                    continue
                flag = True
                len_available_var += 1
            if flag:
                len_available_card += 1
        msg += f'Карточек: {len(json_file)} (Активных: {len_available_card})\nВариаций: {count_var} (Активных: {len_available_var})'
        data = {'card': len(json_file), 'card_active': len_available_card, 'vars': count_var, 'vars_active': len_available_var}
    except Exception as ex:
        msg += f'ERROR: {ex}'
        send_msg_flag = True
    if send_msg_flag:
        send_msg(msg)
    return data


if __name__ == '__main__':
    # get_info_and_send_msg('ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ\n')
    with open('Import_2024_03_06_15_29.json', 'r', encoding='UTF-8') as file:
        json_file = json.load(file)
    count_var = 0
    for i in json_file:
        if 'variations' in i.keys():
            count_var += len(i['variations'])

    len_available_card = 0
    len_available_var = 0
    for i in json_file:
        flag = False
        for j in i['variations']:
            if j['price'] == 0 or j['quantity'] == 0:
                continue
            flag = True
            len_available_var += 1
        if flag:
            len_available_card += 1
    msg = f'Карточек: {len(json_file)} (Активных: {len_available_card})\nВариаций: {count_var} (Активных: {len_available_var})'
    print(msg)
