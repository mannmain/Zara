import asyncio
import time

import aiohttp.client_exceptions
from loguru import logger
from sys import stderr
from datetime import datetime
from abc import ABC
from random import uniform, randint


# from config.config import CHAIN_NAME


def get_user_agent():
    random_version = f"{uniform(520, 540):.2f}"
    return (f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random_version}'
            f' (KHTML, like Gecko) Chrome/121.0.0.0 Safari/{random_version} Edg/121.0.0.0')


class Logger(ABC):
    def __init__(self):
        self.logger = logger
        self.logger.remove()
        logger_format = "<cyan>{time:HH:mm:ss}</cyan> | <level>" "{level: <8}</level> | <level>{message}</level>"
        self.logger.add(stderr, format=logger_format)
        date = datetime.today().date()
        self.logger.add(f"./data/logs/{date}.log", rotation="500 MB", level="INFO", format=logger_format)

    def logger_msg(self, lang_path, msg, type_msg: str = 'info'):
        info = f'{self.__class__.__name__} | {lang_path} |'
        if type_msg == 'info':
            self.logger.info(f"{info} {msg}")
        elif type_msg == 'error':
            self.logger.error(f"{info} {msg}")
        elif type_msg == 'success':
            self.logger.success(f"{info} {msg}")
        elif type_msg == 'warning':
            self.logger.warning(f"{info} {msg}")


class RequestClient(ABC):
    def __init__(self, client):
        # super().__init__()
        self.client = client

    async def make_request(self, name_func: str, method: str = 'GET', url: str = None, headers: dict = None, params: dict = None,
                           data: str = None, json_data: dict = None, resp_type: str = 'text'):
        key_ban = False
        while True:
            try:
                async with self.client.session.request(method=method, url=url, headers=headers) as response:
                    response_text = await response.text()
                    self.logger_msg(self.client.lang_path, msg=f'{name_func} | all nice', type_msg='info')
                    # input(response_text)
                    # print(response_text)
                    if (response_text.find('The operation requested is currently unavailable. Please, try again later.') != -1) or (response_text.find("You don't have permission to access") != -1):
                        self.logger_msg(self.client.lang_path, msg=f'{name_func} | Ban ip', type_msg='error')
                        await asyncio.sleep(60)
                        key_ban = True
                        continue
                    if key_ban:
                        self.logger_msg(self.client.lang_path, msg=f'{name_func} | Unban ip', type_msg='error')
                    if resp_type == 'text':
                        return response_text
                    if resp_type == 'json':
                        try:
                            return await response.json()
                        except Exception as ex:
                            self.logger_msg(self.client.lang_path, msg=f'{name_func} | cant dump json | {response_text} | {ex}', type_msg='error')
                            return None
            except Exception as ex:
                self.logger_msg(self.client.lang_path, msg=f'{name_func} | Запрос не прошел | {ex}', type_msg='error')
