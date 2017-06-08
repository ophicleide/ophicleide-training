import pytest
from pyspark import SparkConf
from pyspark import SparkContext
from pytest_localserver.http import WSGIServer


@pytest.fixture(scope="session")
def spark_context(request):
    conf = (SparkConf().setMaster("local[2]")
            .setAppName("Ophicleide-Training-Test"))
    sc = SparkContext(conf=conf)
    request.addfinalizer(lambda: sc.stop())
    return sc


def temp_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    file = open("tests/resources/test_rdd_input.txt", "r")
    return [file.read()]


@pytest.fixture(scope="session")
def testserver(request):
    server = WSGIServer(application=temp_app)
    server.start()
    request.addfinalizer(server.stop)
    return server
