import ssl

from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from motor.motor_asyncio import AsyncIOMotorCollection

from mongodb.db import db
from view.interfaces import Logger


class Client(Logger):
    def __init__(
            self, county: str, lang: str, proxy_list: list = None,
    ):
        Logger.__init__(self)
        self.proxy_list = proxy_list
        self.proxy_idx = 0
        self.proxy_init = proxy_list[0]
        if self.proxy_init:
            self.session = ClientSession(connector=ProxyConnector.from_url(f'http://{self.proxy_init}', ssl=ssl.create_default_context(), verify_ssl=True))
        else:
            self.session = ClientSession()
        self.county = county
        self.lang = lang
        self.lang_path = f'{county}/{lang}'
        self.collection_items = db.get_collection(f'items_{county}_{lang}')
        # collection.drop()

