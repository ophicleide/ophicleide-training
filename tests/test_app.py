import pytest
from conftest import train_q
import mock
import json
import controllers.default_controller as default_controller
from test_auxiliary_functions import get_fake_collection, get_job
from uuid import UUID, uuid4

pytestmark = pytest.mark.usefixtures("client")


def mock_model_collection():
    collection = get_fake_collection()
    default_controller.model_collection = mock.MagicMock(
        return_value=collection)

    return collection


def mock_queries_collection():
    collection = get_fake_collection()
    default_controller.query_collection = mock.MagicMock(
        return_value=collection)

    return collection


def test_route_root(client):
    response = client.get('/')
    data_in_response = json.loads(response.data)
    assert 'name' in data_in_response
    assert 'version' in data_in_response
    assert 'info' in data_in_response
    assert response.status_code == 200


def test_route_models_get(client):
    collection = mock_model_collection()
    job_a = get_job()
    job_b = get_job()

    collection.insert_one(job_a)
    collection.insert_one(job_b)

    response = client.get('/models')
    data_in_response = json.loads(response.data)

    # Sanitize jobs, and match with expectation
    job_a['id'], job_b['id'] = job_a.pop('_id'), job_b.pop('_id')
    del job_a['callback']
    del job_b['callback']

    assert data_in_response['models'] == [job_a, job_b]
    assert response.status_code == 200


def test_route_models_post(client):
    collection = mock_model_collection()

    job = get_job()
    del job['_id']
    del job['status']

    headers = {'content-type': 'application/json'}
    response = client.post('/models', data=json.dumps(job), headers=headers)

    assert response.status_code == 201

    data_in_response = json.loads(response.data)

    assert data_in_response['status'] == 'training'
    assert data_in_response['urls'] == job['urls']
    assert data_in_response['name'] == job['name']

    mid = UUID(data_in_response['id'])
    data_expected_in_db = collection.find_one({'_id': mid})

    assert data_in_response['status'] == data_expected_in_db['status']
    assert data_in_response['urls'] == data_expected_in_db['urls']
    assert data_in_response['name'] == data_expected_in_db['name']

    # We expect the post request to store data in training queue for the worker
    assert train_q.get() == data_expected_in_db


def test_route_models_id_get_and_id_delete(client):
    collection = mock_model_collection()

    job = get_job()
    mid = job['_id']
    job['_id'] = UUID(job['_id'])

    # Check that appropriate error is retrieved when id does not exist
    response = client.get('/models/' + mid)
    assert response.status_code == 404

    collection.insert_one(job)
    response = client.get('/models/' + mid)
    data_in_response = json.loads(response.data)
    assert 'model' in data_in_response

    model_in_response = data_in_response['model']

    # Match model details to what is expected as response
    del job['callback']
    job['id'] = str(job.pop('_id'))

    assert job == model_in_response

    response = client.delete('/models/' + mid)
    assert response.status_code == 204

    data_in_db = collection.find_one({'_id': mid})
    assert data_in_db is None


# TODO
def test_route_queries_get(client):
    pass


# TODO
def test_route_queries_post(client):
    pass


# TODO
def test_route_queries_id_get(client):
    pass
