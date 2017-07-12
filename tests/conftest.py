import pytest
from pyspark import SparkConf
from pyspark import SparkContext
from pytest_localserver.http import WSGIServer
from test_helpers import mock_model_collection, mock_train_model
import connexion
from multiprocessing import Queue
import conf

train_q = Queue()
result_q = Queue()


@pytest.fixture(scope='session')
def spark_context(request):
    config = (SparkConf().setMaster('local[2]')
              .setAppName('Ophicleide-Training-Test'))
    sc = SparkContext(conf=config)
    request.addfinalizer(lambda: sc.stop())
    return sc


def temp_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    test_file = open('tests/resources/test_url_text_endpoint.txt', 'r')
    return [test_file.read()]


@pytest.fixture(scope='session')
def testserver(request):
    server = WSGIServer(application=temp_app)
    server.start()
    request.addfinalizer(server.stop)
    return server


@pytest.fixture(scope='module')
def client():
    flask_app = connexion.App(__name__, specification_dir='../swagger/')
    conf.init('local[*]', 'mongodb://localhost', train_q, result_q)
    flask_app.add_api('swagger.yaml',
                      arguments={'title': 'Test Word2Vec server'})
    with flask_app.app.test_client() as c:
        yield c


@pytest.fixture(scope='module')
def trained_model(spark_context, testserver):
    db, mid = mock_train_model(spark_context, testserver)
    mock_model_collection(collection=db.models)
    return db, mid
