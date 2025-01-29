import asyncio
import json
from datetime import datetime
from decimal import Decimal

from motor.motor_asyncio import AsyncIOMotorCollection

from config.config import PARSE_PATH_LANG, PARSE_NEW_LANGS, PARSE_MAIN_LANGS
from mongodb.db import db, url_to_category_collection, urls_collection


def format_to_ftp_category(category):
    try:
        parent_id = None
        categories_add_have_product = []
        if category:
            for i in category:
                if not i['name']:
                    continue
                i["parentId"] = parent_id
                categories_add_have_product = [i] + categories_add_have_product
                parent_id = i['id']
        return categories_add_have_product
    except:
        print(f'bad format_to_ftp_category {category}')
        # time.sleep(500)


def get_dict_tree_category(category):
    while True:
        try:
            tree_category_list = []
            for j in category:
                if not j['name']:
                    continue
                tree_category_list.append(j['name'])
            tree_category_str = ' -> '.join(tree_category_list)
            return {tree_category_str: format_to_ftp_category(category)}
        except:
            print(f'bad get_str_tree_category {category}')


def get_needed_extra_details(extra_detail_product):
    return_dict = {}
    for razdel in extra_detail_product:
        flag_to_get_value = False
        subtitles_paragraphs = {}
        subtitle = None
        main_aspect = None
        for block in razdel['components']:
            if block['datatype'] == 'subtitle':
                if block['text']['value'] in ['MATERIALS', 'INGREDIENTS']:
                    main_aspect = block['text']['value']
            if flag_to_get_value:
                if block['datatype'] == 'subtitle':
                    subtitle = block['text']['value']
                if block['datatype'] == 'paragraph':
                    if subtitle:
                        if subtitle not in ['Care for water', 'Recycled polyester']:
                            subtitles_paragraphs[subtitle] = block['text']['value']
            if main_aspect:
                if block['datatype'] == 'paragraph':
                    flag_to_get_value = True
        if main_aspect:
            return_dict[main_aspect] = subtitles_paragraphs
        main_aspect = None
        for block in razdel['components']:
            if block['datatype'] == 'subtitle':
                if block['text']['value'] == "CARE":
                    main_aspect = block['text']['value']
            if main_aspect:
                if block['datatype'] == 'iconList':
                    items = []
                    for item in block['items']:
                        items.append(item['description']['value'])
                    return_dict["Recommendations for care"] = {main_aspect: ", ".join(items)}
    return return_dict


async def construct_translations(prod_id):
    translations = {}
    for path_lang in PARSE_PATH_LANG:
        item = await db.get_collection(f'items_{path_lang[0]}_{path_lang[1]}').find_one({'_id': prod_id})
        # if item:
        print(path_lang, item)
    return translations


def add_to_trans(attr_value_list, translations, key_lang, new_lang_data_dict):
    for attr_trans, value_trans in attr_value_list:
        if value_trans not in new_lang_data_dict[key_lang].values() and attr_trans != value_trans:
            translations[key_lang][attr_trans] = value_trans
    return translations


async def get_rubrics(url_id):
    cat_dict = {}
    async for i in url_to_category_collection.find({'url': url_id}):
        cat_dict.update(get_dict_tree_category(i['cat']))
    return cat_dict


async def construct_files(collection: AsyncIOMotorCollection, currency: str, main_langs: list, limit: int, offset: int):
    lang_parser = main_langs[0][0]
    res_json = []
    part_of_data = [i async for i in collection.find().limit(limit).skip(offset)]
    if not part_of_data:
        return 'last'
    len_part_of_data = len(part_of_data)
    for idx, data_part in enumerate(part_of_data):
        if (idx % 1000 == 0) or (idx == len(part_of_data) - 1):
            print(f"{idx + 1}/{len_part_of_data} {datetime.now()}")
        translations = {}
        new_lang_data_dict = {}
        for path_lang in PARSE_NEW_LANGS:
            item = await db.get_collection(f'items_{path_lang[0]}_{path_lang[1]}').find_one({'_id': data_part['_id']})
            if item:
                trans_data = {}
                if item['name']:
                    name_trans = item['name'][0].upper() + item['name'][1:].lower()
                    if path_lang[1] == 'ru':
                        name_trans += ' ZARA'
                    trans_data = {'name': name_trans}
                for variation in item['data']:
                    trans_data[variation['id']] = {'name': variation['name'], 'properties': {}}
                    try:
                        trans_data[variation['id']]['description'] = variation['description']
                    except:
                        trans_data[variation['id']]['description'] = variation['bundleProducts'][0]['detail']['colors'][0]['description']
                    # if variation['extra_detail']:
                    #     trans_data[variation['id']]['properties'] = get_needed_extra_details(variation['extra_detail'])
                    for size in variation['sizes']:
                        trans_data[variation['id']][f"{size['sku']}"] = {'name': size['name']}

                new_lang_data_dict[path_lang[1]] = trans_data
                translations[path_lang[1]] = {}
                # print(json.dumps(trans_data))

        sku_id_already_add = []
        for path_lang in main_langs:
            item = await db.get_collection(f'items_{path_lang[0]}_{path_lang[1]}').find_one({'_id': data_part['_id']})
            if not item or not item['name']:
                continue
            article = item['_id'][:-5][3:]
            name_product = item['name'][0].upper() + item['name'][1:].lower()

            for key_lang in new_lang_data_dict.keys():
                if "name" in new_lang_data_dict[key_lang]:
                    translations[key_lang][name_product] = new_lang_data_dict[key_lang]['name']

            variations = []
            for variation in item['data']:
                properties = {'': {'Артикул': f'{article[:-3]}/{article[-3:]}'}}
                extra_detail_product = variation['extra_detail']
                if extra_detail_product:
                    properties_add = get_needed_extra_details(extra_detail_product)

                    # if properties_add:
                        # for key_lang in new_lang_data_dict.keys():
                        #     if variation['id'] not in new_lang_data_dict[key_lang].keys():
                        #         continue
                        #     properties_trans = new_lang_data_dict[key_lang][variation['id']]['properties']
                        #     if not properties_trans or not properties_add:
                        #         continue
                        #     if 'Recommendations for care' not in properties_trans.keys() or 'Recommendations for care' not in properties_add.keys():
                        #         continue
                        #     attr_value_list = []
                        #     for key_first_lvl, value_first_lvl in properties_add['Recommendations for care'].items():
                        #         attr_value_list.append()
                        #     attr_value_list = [[var_name, var_name_trans], [description, var_desc_trans]]
                        #     translations = add_to_trans(attr_value_list, translations, key_lang, new_lang_data_dict)

                    properties.update(properties_add)

                var_name = variation['name']
                try:
                    description = variation['description']
                except:
                    description = variation['bundleProducts'][0]['detail']['colors'][0]['description']

                for key_lang in new_lang_data_dict.keys():
                    if variation['id'] in new_lang_data_dict[key_lang].keys():
                        var_name_trans = new_lang_data_dict[key_lang][variation['id']]['name']
                        var_desc_trans = new_lang_data_dict[key_lang][variation['id']]['description']
                        if var_name:
                            attr_value_list = [[var_name, var_name_trans], [description, var_desc_trans]]
                        else:
                            attr_value_list = [[description, var_desc_trans]]
                        translations = add_to_trans(attr_value_list, translations, key_lang, new_lang_data_dict)

                images = []
                for img in variation['mainImgs']:
                    try:
                        images.append(f"https://static.zara.net/photos//{img['path']}/w/1850/{img['name']}.jpg?ts={img['timestamp']}")
                    except:
                        print(f"Error in mainImgs item_id{item['_id']} var_id={variation['id']}")
                if not images:
                    continue
                for size in variation['sizes']:
                    sku = f"{variation['productId']}_{size['name']}"
                    size_name = size['name']

                    for key_lang in new_lang_data_dict.keys():
                        if (variation['id'] in new_lang_data_dict[key_lang].keys()) and (f"{size['sku']}" in new_lang_data_dict[key_lang][variation['id']].keys()):
                            size_name_trans = new_lang_data_dict[key_lang][variation['id']][f"{size['sku']}"]['name']
                            attr_value_list = [[size_name, size_name_trans]]
                            translations = add_to_trans(attr_value_list, translations, key_lang, new_lang_data_dict)

                    if sku in sku_id_already_add:
                        continue
                    sku_id_already_add.append(sku)
                    try:
                        price = Decimal(variation['price'])
                    except:
                        print(f"https://www.zara.com/{lang_parser}/en/{item['_id']}")
                        continue
                    quantity = None
                    if size['availability'] != 'in_stock' and size['availability'] != 'low_on_stock':
                        quantity = 0
                    params = {}
                    if var_name:
                        params['Colour'] = var_name
                    if size_name:
                        params['Size'] = size_name
                    variation_one = {
                        "name": f"{name_product}",
                        "images": images,
                        "price": float(price / Decimal('100')),
                        "currency": currency,
                        "quantity": quantity,
                        "sku": sku,
                        "description": description,
                    }
                    if properties:
                        variation_one['properties'] = properties
                    if params:
                        variation_one['params'] = params
                    variations.append(variation_one)
            if not variations:
                continue

            # url_data = await urls_collection.find_one({'_id': data_part['_id']})
            cat_dict = await get_rubrics(data_part['_id'])
            res_json_to_append = {
                "name": f"{name_product}",
                "brand": "Zara",
                "externalId": f"https://www.zara.com/{lang_parser}/en/{item['_id']}",  # заменить на full url
                # "externalId": f"https://www.zara.com/tr/en/{url_data['url_full']}",
                "variations": variations
            }
            if translations:
                res_json_to_append['translations'] = translations
            # if name_rus_product:
            #     res_json_to_append['nameRu'] = name_rus_product + ' ZARA'
            # if description_rus:
            #     res_json_to_append['descriptionRu'] = description_rus
            #
            keys_rubrics = list(cat_dict.keys())
            res_json_to_append["rubrics"] = cat_dict[keys_rubrics[0]]
            if len(keys_rubrics) > 1:
                alternative_rubrics = []
                for rubric_num in range(1, len(keys_rubrics)):
                    alternative_rubrics.append(cat_dict[keys_rubrics[rubric_num]])
                res_json_to_append["alternativeRubrics"] = alternative_rubrics
            res_json.append(res_json_to_append)
    with open('ftp/json.json', 'w', encoding='utf-8') as file:
        json.dump(res_json, file)
    print(f'Construct {len(part_of_data)} items of {limit=} and {offset=}')


async def construct_files_2(collection: AsyncIOMotorCollection, limit: int, offset: int):
    res_json = []
    part_of_data = [i async for i in collection.find().limit(limit).skip(offset)]
    if not part_of_data:
        return True
    for i in part_of_data:
        if i['name']:
            article = i['_id'][: -5][3:]
            name_product = i['name'][0].upper() + i['name'][1:].lower()
            # if i.name_rus_product:
            #     name_rus_product = i.name_rus_product[0].upper() + i.name_rus_product[1:].lower()
            # else:
            #     name_rus_product = ''
            variations = []
            # description_rus = ''
            for variation in i['data']:
                properties = {'': {'Артикул': f'{article[:-3]}/{article[-3:]}'}}
                extra_detail_product = variation['extra_detail']
                if extra_detail_product:
                    properties.update(get_needed_extra_details(extra_detail_product))
                images = []
                for img in variation['mainImgs']:
                    images.append(f"https://static.zara.net/photos//{img['path']}/w/1850/{img['name']}.jpg?ts={img['timestamp']}")
                for size in variation['sizes']:
                    try:
                        price = Decimal(variation['price'])
                    except:
                        print(i.link_product)
                        continue
                    quantity = None
                    if size['availability'] != 'in_stock' and size['availability'] != 'low_on_stock':
                        quantity = 0
                    try:
                        description = variation['description']
                    except:
                        description = variation['bundleProducts'][0]['detail']['colors'][0]['description']
                    variation_one = {
                        "name": f"{name_product}",
                        "nameEn": f"{name_product}",
                        "images": images,
                        "params": {
                            "Colour": variation['name'],
                            "Size": size['name'],
                        },
                        "price": float(price / Decimal('100')),
                        "currency": "TRY",
                        "quantity": quantity,
                        "sku": f"{variation['productId']}_{size['name']}",
                        "description": description,
                    }
                    # if name_rus_product:
                    #     variation_one['nameRu'] = name_rus_product + ' ZARA'
                    if properties:
                        variation_one['properties'] = properties
                    # if 'description_rus' in list(variation.keys()):
                    #     description_rus = variation['description_rus']
                    #     variation_one["descriptionRu"] = variation['description_rus']
                    variations.append(variation_one)
            translations = await construct_translations(i['_id'])
            res_json_to_append = {
                "name": f"{name_product}",
                "nameEn": f"{name_product}",
                "brand": "Zara",
                "externalId": f"https://www.zara.com/tr/en/{i['_id']}",  # заменить на full url
                "variations": variations
            }
            # if name_rus_product:
            #     res_json_to_append['nameRu'] = name_rus_product + ' ZARA'
            # if description_rus:
            #     res_json_to_append['descriptionRu'] = description_rus

            # keys_rubrics = list(json.loads(i.categories_have_product).keys())
            # res_json_to_append["rubrics"] = json.loads(i.categories_have_product)[keys_rubrics[0]]
            # if len(keys_rubrics) > 1:
            #     alternative_rubrics = []
            #     for rubric_num in range(1, len(keys_rubrics)):
            #         alternative_rubrics.append(json.loads(i.categories_have_product)[keys_rubrics[rubric_num]])
            #     res_json_to_append["alternativeRubrics"] = alternative_rubrics
            res_json.append(res_json_to_append)
    with open('json_upload_rus.json', 'w', encoding='utf-8') as file:
        json.dump(res_json, file)
    print(f'Construct {len(part_of_data)} items of {limit=} and {offset=}')


async def test(collection: AsyncIOMotorCollection, limit: int, offset: int):
    c = 0
    part_of_data = [i async for i in collection.find().limit(limit).skip(offset)]
    if not part_of_data:
        return True
    for i in part_of_data:
        print(i)
    # for
        if i['name']:
            flag = False
            for variation in i['data']:
                for size in variation['sizes']:
                    if i["_id"] == '-p04391714.html':
                        print(size['availability'])
                    quantity = None
                    if size['availability'] != 'in_stock' and size['availability'] != 'low_on_stock':
                    # if size['availability'] != 'in_stock':
                        quantity = 0
                        # if size['availability'] not in ['out_of_stock', 'coming_soon', 'low_on_stock']:
                        # if size['availability'] == 'low_on_stock':
                        #     print(i['_id'])
                        #     print(size['name'])
                        #     print(variation['name'])
                        #     input(size['availability'])
                        continue
                    flag = True
                    break
                if flag:
                    break
            if flag:
                c += 1
            # else:
            #     input(f'https://www.zara.com/tr/en/{i["_id"]}')
    print(f'{c=}')


# asyncio.run(test(db.get_collection('items_tr'), 99999999999, 0))
# asyncio.run(construct_files(db.get_collection('items_es_en'), 10000, 0))
