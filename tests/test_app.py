from conftest import train_q
import json
from test_helpers import get_job
from uuid import UUID
from test_helpers import mock_model_collection, mock_queries_collection
from test_helpers import submit_post_query, submit_get_req, compare_dicts


def test_route_root(client):
    """ Test if server info is in response.

    :param client: a flask test client.
    """
    response = client.get('/')
    res_data = json.loads(response.data)
    assert response.status_code == 200
    assert all([key in res_data for key in ['name', 'version', 'info']])


def test_route_models_get(client):
    """ Test if get request to /models responds with models in the db.

    :param client: a flask test client.
    """
    collection = mock_model_collection()
    job_a = get_job()
    job_b = get_job()

    collection.insert_one(job_a)
    collection.insert_one(job_b)

    res_data = submit_get_req(client, '/models')

    # Sanitize jobs, and match with expectation
    job_a['id'], job_b['id'] = str(job_a.pop('_id')), str(job_b.pop('_id'))
    del job_a['callback']
    del job_b['callback']

    assert res_data['models'] == [job_a, job_b]


def test_route_models_post(client):
    """ Test if post request to /models updates db and sends appropriate json
    data in response. Also ensure that model data is fed into the outgoing
    multiprocessing Queue().

    :param client: a flask test client.
    """
    collection = mock_model_collection()

    job = get_job()
    del job['_id']
    del job['status']

    headers = {'content-type': 'application/json'}
    response = client.post('/models', data=json.dumps(job), headers=headers)

    assert response.status_code == 201

    res_data = json.loads(response.data)

    # Note: Api specifies 'callback' to be included in response but
    # default_controller.create_training_model does not include it.
    job['status'] = 'training'
    assert 'id' in res_data
    assert compare_dicts(job, res_data, ['name', 'status', 'urls'])

    mid = UUID(res_data['id'])

    # Verify data is inserted into the db
    db_data = collection.find_one({'_id': mid})
    assert compare_dicts(res_data, db_data, ['status', 'urls', 'name'])

    # We expect the post request operation to store data in queue for worker
    assert train_q.get() == db_data


def test_route_models_id_get(client):
    """ Test get request to /models/{id} route. Test response json data
    validity.

    :param client: a flask test client.
    """
    collection = mock_model_collection()

    job = get_job()
    mid = str(job['_id'])

    # Model does not exist, error is expected
    response = client.get('/models/' + mid)
    assert response.status_code == 404

    # Insert data into db for a valid response
    collection.insert_one(job)

    res_data = submit_get_req(client, '/models/', route_id=mid)

    assert 'model' in res_data
    res_model = res_data['model']

    # Match model details to what is expected as response
    del job['callback']
    job['id'] = str(job.pop('_id'))

    assert job == res_model


def test_route_models_id_delete(client):
    """ Test delete request to /models/{id} route. Ensure that the data
    inserted is deleted after a delete request to /models/{id}.

    :param client: a flask test client.
    """
    collection = mock_model_collection()
    job = get_job()
    mid = str(job['_id'])

    collection.insert_one(job)

    db_data = collection.find_one({'_id': job['_id']})
    assert db_data is not None

    response = client.delete('/models/' + mid)
    assert response.status_code == 204

    db_data = collection.find_one({'_id': mid})
    assert db_data is None


def test_route_queries_post(client, trained_model):
    """ Test post request to /queries. First train a model, then perform
    request, ensure response query contains all pertinent values.

    pre-condition: the test assumes worker.py is tested and working in order to
    query against an appropriate model with relevant data.

    :param client: a flask test client fixture.
    :param trained_model: a tuple containing the id and (mocked) db name of a
    trained model.
    """
    db, mid = trained_model

    mock_model_collection(collection=db.models)
    mock_queries_collection()

    expected_word = 'one'
    res_data = submit_post_query(client, mid, expected_word)

    assert 'query' in res_data
    query = res_data['query']

    expected_keys = ['id', 'word', 'results', 'modelName', 'model']
    assert all([(k in query) for k in expected_keys])

    assert query['model'] == str(mid)
    assert query['modelName'] == get_job()['name']
    assert query['word'] == expected_word

    results = query['results']
    assert isinstance(results, list)
    assert all([
        (isinstance(pair[0], float) and isinstance(pair[1], unicode))
        for pair in results])


def test_route_queries_post_db_update(client, trained_model):
    """ Test db update from post request to /queries.

    pre-condition: the test assumes worker.py is tested and working in order to
    query against an appropriate model with relevant data.

    :param client: a flask test client fixture.
    :param trained_model: a tuple containing the id and (mocked) db name of a
    trained model.
    """
    db, mid = trained_model

    mock_model_collection(collection=db.models)
    collection = mock_queries_collection()

    expected_word = 'one'
    res_data = submit_post_query(client, mid, expected_word)
    expected_db_data = res_data['query']

    expected_db_data['_id'] = UUID(expected_db_data.pop('id'))

    results = [(pair[0], pair[1]) for pair in expected_db_data['results']]
    expected_db_data['results'] = results

    # Test data is in db
    db_data = collection.find_one({'_id': expected_db_data['_id']})

    assert db_data is not None

    expected_keys = ['_id', 'model', 'modelName', 'results', 'word']
    assert compare_dicts(expected_db_data, db_data, expected_keys)


def test_route_queries_get(client, trained_model):
    """ Test get request to /queries. Submit two queries via post request, and
    test if they are retrieved via a get request as per api specs.

    :param client: a flask test client fixture.
    :param trained_model: a tuple containing the id and (mocked) db name of a
    trained model.
    """
    db, mid = trained_model

    mock_model_collection(collection=db.models)
    mock_queries_collection()

    post_response_data = submit_post_query(client, mid, 'one')
    post_data_a = post_response_data['query']

    post_response_data = submit_post_query(client, mid, 'born')
    post_data_b = post_response_data['query']

    data_in_response = submit_get_req(client, '/queries')
    assert 'queries' in data_in_response

    queries = data_in_response['queries']
    assert isinstance(queries, list) and len(queries) == 2

    # id, model, word should match data submitted via post request
    get_data_a, get_data_b = queries[0], queries[1]
    expected_keys = ['id', 'model', 'word']
    assert compare_dicts(get_data_a, post_data_a, expected_keys)
    assert compare_dicts(get_data_b, post_data_b, expected_keys)


def test_route_queries_id_get(client, trained_model):
    """ Test get request to /queries/{id}. Submit a query via post request, and
    test if it is retrieved via a get request as per api specs.

    :param client: a flask test client fixture.
    :param trained_model: a tuple containing the id and (mocked) db name of a
    trained model.
    """
    db, mid = trained_model

    mock_model_collection(collection=db.models)
    mock_queries_collection()

    post_response_data = submit_post_query(client, mid, 'one')
    post_res_query = post_response_data['query']
    query_id = post_res_query['id']

    data_in_response = submit_get_req(client, '/queries/', route_id=query_id)

    get_res_query = data_in_response['query']

    expected_keys = ['id', 'word', 'model', 'modelName']
    assert compare_dicts(get_res_query, post_res_query, expected_keys)
