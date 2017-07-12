import mongomock
from uuid import uuid4
from worker import update_model
from multiprocessing import Queue
import controllers.default_controller as default_controller
import mock
import json


def get_fake_collection():
    m = get_fake_mongo_client()
    return m['testing'].collection


def get_fake_mongo_client(host_arg=None, port_arg=None):
    return mongomock.MongoClient(host=host_arg, port=port_arg)


def get_job():
    job = {'urls': ['http://testurl'], 'name': 'Test_models_route',
           "_id": uuid4(), 'status': 'training',
           'callback': 'http://test_callback'}
    return job


def mock_model_collection(collection=None):
    if collection is None:
        collection = get_fake_collection()
    default_controller.model_collection = mock.MagicMock(
        return_value=collection)
    return collection


def mock_queries_collection(collection=None):
    if collection is None:
        collection = get_fake_collection()
    default_controller.query_collection = mock.MagicMock(
        return_value=collection)
    return collection


def mock_train_model(spark_context, testserver):
    """Pre-condition: worker.update_one is assumed to be working."""
    inq = Queue()
    outq = Queue()

    job = get_job()
    job['urls'] = [testserver.url]

    db = get_fake_mongo_client().ophicleide
    db.models.insert_one(job)

    inq.put(job)
    update_model(spark_context, inq, outq, db, 'http://testurl')

    return db, job['_id']


def submit_post_query(client, mid, word, expected_status_code=201):
    """A word must have synonyms"""
    query = {'model': str(mid), 'word': word}
    headers = {'content-type': 'application/json'}
    response = client.post('/queries', data=json.dumps(query), headers=headers)
    assert response.status_code == expected_status_code
    return json.loads(response.data)


def submit_get_req(client, route, status_code=200, route_id=''):
    response = client.get(route + route_id)
    assert response.status_code == status_code
    data_in_response = json.loads(response.data)
    return data_in_response


def compare_dicts(expected, actual, expected_keys):
    for k in expected_keys:
        assert k in actual
        assert expected[k] == actual[k]
    return True
