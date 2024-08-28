import asyncio
import json
import os
import time
from datetime import datetime

from ftp.ftp import upload_file
from mongodb.db import db, client_async
from tg.notification import get_info_and_send_msg, finally_info_and_send_msg, end_and_send_msg, start_and_send_msg, \
    send_msg
from view.request_api import starter_parse
from view.structure import construct_files
from config.config import *


async def construct_and_upload_func(ftp_host, ftp_user, ftp_password, collection, currency: str, main_lang: list,):
    data_finally = {'card': 0, 'card_active': 0, 'vars': 0, 'vars_active': 0}
    skip = 0
    while True:
        status = await construct_files(collection, currency, [main_lang], STEP_LEN_UPLOAD, skip)
        if status == 'last':
            break
        skip += STEP_LEN_UPLOAD
        upload_file(ftp_host, ftp_user, ftp_password)
        data = get_info_and_send_msg(send_msg_flag=False)
        if data:
            for i in data.keys():
                data_finally[i] += data[i]
        await asyncio.sleep(60)
    finally_info_and_send_msg(data_finally, f'Currency: {currency}\n')


async def main():
    start_and_send_msg()
    try:
        # await client_async.drop_database('Zara')
        await starter_parse()
        await construct_and_upload_func(
            FTP_HOST_TR, FTP_USER_TR, FTP_PASSWORD_TR, db.get_collection('items_tr_en'), 'TRY', PARSE_MAIN_LANGS[1]
        )
        await construct_and_upload_func(
            FTP_HOST_ES, FTP_USER_ES, FTP_PASSWORD_ES, db.get_collection('items_es_en'), 'EUR', PARSE_MAIN_LANGS[0]
        )
    except Exception as ex:
        print(f"error: {ex}")
        msg = f'{TG_NAME_PARSE}\n{datetime.now().strftime("%m.%d %H:%M")}\n[ОШИБКА]\nex: {ex}'
        send_msg(msg)
    end_and_send_msg()


def start():
    asyncio.get_event_loop().run_until_complete(main())


if __name__ == '__main__':
    import schedule
    while True:
        asyncio.get_event_loop().run_until_complete(main())

    # schedule.every().day.at(TIME_TO_START).do(start)
    # # schedule.every(5).seconds.do(start)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)  # wait one m  inute
    # asyncio.run(main())
