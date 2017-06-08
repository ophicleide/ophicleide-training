import pytest
import connexion
import mock
import mongomock
from multiprocessing import Queue
import conf
import controllers.default_controller as default_controller

flask_app = connexion.App(__name__, specification_dir='../swagger/')
train_q = Queue()
result_q = Queue()
conf.init("local[*]", "mongodb://localhost", train_q, result_q)
flask_app.add_api('swagger.yaml', arguments={'title': 'Test Word2Vec server'})


@pytest.fixture(scope='module')
def client():
    with flask_app.app.test_client() as c:
        yield c


def get_fake_collection():
    m = mongomock.MongoClient()
    return m['models'].collection


def test_route_root(client):
    response = client.get('/')
    assert response.status_code == 200


def test_route_models(client):
    collection = get_fake_collection()
    default_controller.model_collection = \
        mock.MagicMock(return_value=collection)
    default_controller.query_collection = \
        mock.MagicMock(return_value=collection)

    response = client.get('/models')
    assert response.status_code == 200
