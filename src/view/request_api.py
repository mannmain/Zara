import asyncio
import json
import ssl
import time
import uuid

from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup

from config.config import PARSE_MAIN_LANGS, PARSE_PATH_LANG, PROXY
from config.helper import split_list
from mongodb.db import *
from view.client import Client
from view.interfaces import *


class ParserUrls(Logger, RequestClient):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.base_url = 'https://www.zara.com/'

    def get_sub_categories(self, categories, parent_categories):
        for category in categories:
            if category['subcategories']:
                return_categories = self.get_sub_categories(category['subcategories'], parent_categories + [{'name': category['name'], 'id': str(category['id'])}])
                for return_category in return_categories:
                    yield return_category
            else:
                yield parent_categories + [{'name': category['name'], 'id': str(category['id'])}]

    async def request_all_categories(self):
        url = f'{self.base_url}{self.client.county}/en/categories?ajax=true'
        while True:
            try:
                async with self.client.session.request(method='GET', url=url, headers={'User-Agent': get_user_agent()}) as response:
                    response_text = await response.text()
                    if (response_text.find('The operation requested is currently unavailable. Please, try again later.') != -1) or (response_text.find("You don't have permission to access") != -1):
                        self.logger_msg(self.client.lang_path, msg=f'Ждем 130 сек', type_msg='warning')
                        await asyncio.sleep(130)
                try:
                    response_json = await response.json()
                    categories_list = self.get_sub_categories(response_json['categories'], [])
                    await insert_to_db([{'_id': self.client.county, 'data': list(categories_list)}], cats_collection)
                    return
                except:
                    self.logger_msg(self.client.lang_path, msg=f'Ждем 600 сек', type_msg='warning')
                    await asyncio.sleep(600)
            except Exception as ex:
                self.logger_msg(self.client.lang_path, msg=f'Запрос не прошел get_all_categories | {ex}', type_msg='error')
                await asyncio.sleep(10)

    async def request_url_category(self, category_list: list):
        key_ban = False
        name_func = self.request_url_category.__name__
        url = f'https://www.zara.com/tr/en/category/{category_list[-1]["id"]}/products?ajax=true'
        while True:
            try:
                async with self.client.session.request(method='GET', url=url, headers={'User-Agent': get_user_agent()}) as response:
                    response_text = await response.text()
                    # print(response_text)
                    if (response_text.find('The operation requested is currently unavailable. Please, try again later.') != -1) or (response_text.find("You don't have permission to access") != -1):
                        self.logger_msg(self.client.lang_path, msg=f'{name_func} | Ban ip', type_msg='error')
                        await asyncio.sleep(60)
                        key_ban = True
                        continue
                    try:
                        response_json = await response.json()
                        product_groups = response_json['productGroups']
                        if key_ban:
                            self.logger_msg(self.client.lang_path, msg=f'{name_func} | Unban ip', type_msg='error')
                        if not product_groups:
                            return
                        return response_json['productGroups'][0]['elements']
                    except Exception as ex:
                        self.logger_msg(self.client.lang_path, msg=f'{name_func} | cant dump json | {response_text} | {ex} | {category_list}', type_msg='error')
                        return
            except Exception as ex:
                self.logger_msg(self.client.lang_path, msg=f'{name_func} | Запрос не прошел | {ex}', type_msg='error')

    async def parse_url_category(self, category_list):
        products = await self.request_url_category(category_list)
        if not products:
            return
        update_categories = []
        update_urls = []
        for commercial_components in products:
            if 'commercialComponents' in commercial_components.keys():
                for product in commercial_components['commercialComponents']:
                    if ('seo' in product.keys()) and (product['seo']):
                        seo = product['seo']
                        if ('seoProductId' in seo.keys()) and (seo['seoProductId']):
                            url = f"-p{seo['seoProductId']}.html"
                            full_url = url
                            if 'keyword' in seo.keys():
                                full_url = f"{seo['keyword']}{full_url}"
                            if 'discernProductId' in seo.keys():
                                full_url += f"?v1={seo['discernProductId']}"
                            while True:  # Правда бесконечная, так как обязательно должно выполниться
                                try:
                                    cat_ids = '_'.join([str(i['id']) for i in category_list])
                                    break
                                except:
                                    self.logger_msg(self.client.lang_path, msg=f'Взятие id categories | {category_list}', type_msg='error')
                            update_categories.append({'_id': f'{url}_{cat_ids}', 'url': url, 'cat': category_list})
                            update_urls.append({'_id': url, 'url_full': full_url})
        if update_categories:
            await insert_to_db(update_categories, url_to_category_collection)
        if update_urls:
            await insert_to_db(update_urls, urls_collection)

    async def start_parse_urls_categories(self):
        url_list = await cats_collection.find_one({'_id': self.client.county})
        len_url_list = len(url_list['data'])
        step = 1
        finish_count = 0
        split_generator = split_list(url_list['data'], step)
        for part_of_categories in split_generator:
            finish_count += step
            tasks = [self.parse_url_category(i) for i in part_of_categories]
            await asyncio.gather(*tasks)
            self.logger_msg(self.client.lang_path, msg=f'Пройдено Urls {finish_count}/{len_url_list} категорий', type_msg='info')
        # await self.parse_url_category(url_list['data'][0])

    async def start_get_urls(self):
        await self.request_all_categories()
        await self.start_parse_urls_categories()


class ParserItems(Logger):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.base_url = 'https://www.zara.com/'

    async def make_request(self, name_func: str, method: str = 'GET', url: str = None, headers: dict = None, params: dict = None,
                           data: str = None, json_data: dict = None, resp_type: str = 'text', bm_verify: bool = False,
                           cookie: str = ''):
        url_to_req = url
        if bm_verify:
            url_to_req += f'&bm-verify='
        key_ban = False
        _headers = {
            'authority': 'www.zara.com',
            'accept-language': 'ru,en;q=0.9,zh;q=0.8',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            # 'cookie': cookie,
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': f'{get_user_agent()}',
        }
        headers = _headers.copy()
        # if cookie:
        #     headers['cookie'] = cookie
        while True:
            try:
                # async with self.client.session.request(method=method, url=url_to_req, headers=headers) as response:
                # async with ClientSession(headers=headers, connector=ProxyConnector.from_url(f'http://{self.client.proxy_init}', ssl=ssl.create_default_context(), verify_ssl=True)) as session:
                async with ClientSession(headers=headers) as session:
                    async with session.request(headers=headers, method=method, url=url_to_req) as response:
                        response_text = await response.text()
                        # self.logger_msg(self.client.lang_path, msg=f'{name_func} | all nice', type_msg='info')
                        # input(response_text)
                        # print(response_text)
                        if (response_text.find('The operation requested is currently unavailable. Please, try again later.') != -1) or (response_text.find("You don't have permission to access") != -1):
                            headers = _headers.copy()
                            self.logger_msg(self.client.lang_path, msg=f'{name_func} | Ban ip | {url_to_req}', type_msg='error')
                            await asyncio.sleep(60)
                            key_ban = True
                            # return None  # поставил возврат, потому что не должно впринципе банить, а сылки, которые уже не существуют отдают такой же текст, как и когда забанили
                            continue  # до return был continue
                        if bm_verify:
                            soup = BeautifulSoup(response_text, 'lxml')
                            refresh_link = soup.find('meta', attrs={'http-equiv': "refresh"})
                            if refresh_link:
                                content_url = refresh_link['content']
                                self.logger_msg(self.client.lang_path, msg=f'{url} | refrest_link', type_msg='warning')
                                url_to_req = self.base_url + content_url[content_url.find("URL='/") + 6:len(content_url) - 1]
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

    async def get_extra_detail_from_product(self, product_id: str):
        name_func = self.get_extra_detail_from_product.__name__
        url = f'{self.base_url}{self.client.lang_path}/product/{product_id}/extra-detail?ajax=true'
        response_json = await self.make_request(name_func=name_func, method='GET', url=url, resp_type='json', bm_verify=True)
        return response_json

    async def request_extra_and_parse_info(self, info_about_product):
        name = info_about_product['product']['name']
        new_info_about_product = []
        for one_product in info_about_product['product']['detail']['colors']:
            extra_detail = await self.get_extra_detail_from_product(one_product['productId'])
            one_product["extra_detail"] = extra_detail
            new_info_about_product.append(one_product)
        return name, new_info_about_product

    async def get_data_item(self, url_id: str, url_full: str):
        name_func = self.get_data_item.__name__
        url = f'{self.base_url}{self.client.lang_path}/{url_full}'
        # url = f'https://www.zara.com/tr/en/stoneware-dinner-plate-p42448200.html?v1=312377191&v2=2357912'
        cookies_dict = self.client.session.cookie_jar.filter_cookies(self.base_url)
        cookie = ''
        if 'ak_bmsc' in cookies_dict.keys():
            cookie = f'ak_bmsc={str(cookies_dict["ak_bmsc"]).split("ak_bmsc=")[-1]}'
        response_text = await self.make_request(name_func=name_func, method='GET', url=url, resp_type='text', bm_verify=True, cookie=cookie)
        if not response_text:
            return None
        soup = BeautifulSoup(response_text, 'lxml')
        script_text = soup.find('body').find('script', attrs={'data-compress': "true"}).text
        info_about_product = json.loads(script_text[script_text.find('window.zara.viewPayload = ') + len('window.zara.viewPayload = '):-1])
        if info_about_product and 'product' in info_about_product.keys():
            name, new_info_about_product = await self.request_extra_and_parse_info(info_about_product)
            if new_info_about_product:
                await insert_to_db([{'_id': url_id, 'name': name, 'data': new_info_about_product}], self.client.collection_items)

    async def start_parse_items(self):
        # await ParserUrls(self.client).request_url_category([{"name": "WOMAN", "id": "853236"}, {"name": "/// NEW", "id": "2352540"}])
        # await self.get_data_item('-p03253325.html', 'ribbed-vest-top-p03253325.html?v1=347810709')
        len_url_list = await urls_collection.count_documents({})
        step = 1
        finish_count = 0
        if self.client.lang_path == 'kz/ru':
            finish_count = 7407
        # async for i in urls_collection.find():
        #     finish_count += step
        #     await self.get_data_item(i['_id'], i['url_full'])
        #     self.logger_msg(self.client.lang_path, msg=f'Пройдено Items {finish_count}/{len_url_list} товаров', type_msg='info')
        while True:
            tasks = [self.get_data_item(i['_id'], i['url_full']) async for i in urls_collection.find().limit(step).skip(finish_count)]
            if not tasks:
                break
            await asyncio.gather(*tasks)
            self.logger_msg(self.client.lang_path, msg=f'Пройдено Items {finish_count + step}/{len_url_list} товаров', type_msg='info')
            finish_count += step


async def starter_parse():
    # for idx, country_lang in enumerate(PARSE_MAIN_LANGS):
    #     client = Client(country_lang[0], country_lang[1], proxy=PROXY)
    #     worker = ParserUrls(client)
    #     await worker.start_get_urls()
    #     await client.session.close()
    #     if idx == len(PARSE_MAIN_LANGS) - 1:
    #         client.logger_msg(client.lang_path, msg=f'Urls success parsed', type_msg='success')
    for idx, country_lang in enumerate([['kz', 'ru'], ['es', 'en'], ['tr', 'en']]):
        client = Client(country_lang[0], country_lang[1], proxy=PROXY)
        worker = ParserItems(client)
        await worker.start_parse_items()
        await client.session.close()
        if idx == len(PARSE_PATH_LANG) - 1:
            client.logger_msg(client.lang_path, msg=f'Items success parsed', type_msg='success')


if __name__ == '__main__':
    asyncio.run(starter_parse())
