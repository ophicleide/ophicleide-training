import mongomock
from uuid import uuid4


def get_fake_collection():
    m = get_fake_mongo_client()
    return m['testing'].collection


def get_fake_mongo_client(host_arg=None, port_arg=None):
    return mongomock.MongoClient(host=host_arg, port=port_arg)


def get_job():
    job = {'urls': ['http://testurl'], 'name': 'Test_models_route',
           "_id": str(uuid4()), 'status': 'training',
           'callback': 'http://test_callback'}
    return job
