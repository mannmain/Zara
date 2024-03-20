import motor.motor_asyncio
from pymongo.errors import BulkWriteError, WriteError
from config.config import MONGODB_URL, NAME_DB
from pymongo.collection import Collection


# client = MongoClient(MONGODB_URL)
# db = client[NAME_DB]
client_async = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client_async.get_database(NAME_DB)

cats_collection = db.get_collection('cats')
url_to_category_collection = db.get_collection('url_to_category')
urls_collection = db.get_collection('urls')
name_collection = db.get_collection('product2')


async def insert_to_db(data_list, collection):
    try:
        await collection.insert_many(data_list, ordered=False, bypass_document_validation=True)
    except BulkWriteError as e:
        panic_list = list(filter(lambda x: x['code'] != 11000, e.details['writeErrors']))
        if len(panic_list) > 0:
            print(f"these are not duplicate errors {panic_list}")
            print(f"Articles bulk insertion error {e}")
    except Exception as ex:
        print(f"db insert new error {ex}")
