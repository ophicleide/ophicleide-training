import pytest
import worker
from pyspark.mllib.feature import Word2VecModel
from pyspark.rdd import PipelinedRDD
from mock import patch
from test_auxiliary_functions import get_job, get_fake_mongo_client
from multiprocessing import Queue, Process
import pymongo

from worker import workloop

pytestmark = pytest.mark.usefixtures("spark_context")


def test_cleanstr():
    assert worker.cleanstr("") == ""
    assert worker.cleanstr("!@T#$%^&e*()-.;'S{}[]t/`~-=+_") == "t e s t"
    assert worker.cleanstr("  :tesTing' cleAnsTr.  ") == "testing cleanstr"


def test_train_return_type(spark_context, testserver):
    urls = [testserver.url]
    result = worker.train(spark_context, urls)
    assert isinstance(result, Word2VecModel)


def test_url2rdd_return_type(spark_context, testserver):
    result = worker.url2rdd(spark_context, testserver.url)
    assert isinstance(result, PipelinedRDD)


@patch('worker.SparkContext')
@patch('pymongo.MongoClient')
def test_train_output(mc, sc, spark_context, testserver):
    sc.return_value = spark_context
    mc.return_value = get_fake_mongo_client()

    inq = Queue()
    outq = Queue()

    job = get_job()
    job['urls'] = [testserver.url]

    expected_id = job['_id']
    expected_name = job['name']

    # returns a mock mongo database
    db = pymongo.MongoClient("http://testurl").ophicleide

    db.models.insert_one(job)
    inq.put(job)

    p = Process(target=workloop, args=("local[2]", inq, outq,
                                       "http://testurl"))
    p.start()

    # wait for worker to spin up
    outq.get()

    # wait for worker to train model
    result = outq.get()
    p.terminate()
    mid = result[0]
    model_name = result[1]

    assert model_name == expected_name
    assert mid == expected_id
