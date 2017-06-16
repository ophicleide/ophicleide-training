import pytest
from pyspark import SparkConf
from pyspark import SparkContext
from pytest_localserver.http import WSGIServer
import connexion
from multiprocessing import Queue
import conf


@pytest.fixture(scope="session")
def spark_context(request):
    config = (SparkConf().setMaster("local[2]")
              .setAppName("Ophicleide-Training-Test"))
    sc = SparkContext(conf=config)
    request.addfinalizer(lambda: sc.stop())
    return sc


def temp_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    test_file = open("tests/resources/test_rdd_input.txt", "r")
    return [test_file.read()]


@pytest.fixture(scope="session")
def testserver(request):
    server = WSGIServer(application=temp_app)
    server.start()
    request.addfinalizer(server.stop)
    return server


flask_app = connexion.App(__name__, specification_dir='../swagger/')
train_q = Queue()
result_q = Queue()
conf.init('local[*]', 'mongodb://localhost', train_q, result_q)
flask_app.add_api('swagger.yaml', arguments={'title': 'Test Word2Vec server'})


@pytest.fixture(scope='module')
def client():
    with flask_app.app.test_client() as c:
        yield c
