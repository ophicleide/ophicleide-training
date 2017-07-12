import worker
from pyspark.mllib.feature import Word2VecModel
from pyspark.rdd import PipelinedRDD
from mock import patch
from test_helpers import get_job, get_fake_mongo_client
from multiprocessing import Queue, Process
from bson.binary import Binary
import pymongo
import json


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


def test_update_model_db(spark_context, testserver):
    """ Test update_model. Ensure model collection is updated and the
    appropriate data is stored.

    :param spark_context: a pre-configured spark context fixture.
    :param testserver: a WSGIServer fixture.
    """
    inq = Queue()
    outq = Queue()

    job = get_job()
    job['urls'] = [testserver.url]

    expected_id = job['_id']

    db = get_fake_mongo_client().ophicleide
    db.models.insert_one(job)
    inq.put(job)

    worker.update_model(spark_context, inq, outq, db, 'http://testurl')

    outq.get()

    data_in_db = db.models.find_one({'_id': expected_id})

    expected_keys = ['_id', 'model', 'status', 'last_updated']

    assert all([key in data_in_db for key in expected_keys])
    assert data_in_db['_id'] == expected_id
    assert data_in_db['status'] == 'ready'

    model = data_in_db['model']

    assert 'words' in model and 'zndvecs' in model

    words, zn = model['words'], model['zndvecs']

    assert isinstance(words, list)
    assert isinstance(zn, Binary)

    with open('tests/resources/test_training_model_words_list.json') \
            as json_data:
        expected_data = json.load(json_data)
        assert words == expected_data['words']


@patch('worker.SparkContext')
@patch('pymongo.MongoClient')
def test_workloop_output_in_queue(mc, sc, spark_context, testserver):
    """ Test workloop. Start a workloop process and ensure the output queue
    receives the appropriate response.

    :param mc: a patched pymongo.MongoClient
    :param sc: a mocked worker.SparkContext
    :param spark_context: a pre-configured spark context fixture.
    :param testserver: a WSGIServer fixture.
    """
    sc.return_value = spark_context
    mc.return_value = get_fake_mongo_client()

    inq = Queue()
    outq = Queue()

    job = get_job()
    job['urls'] = [testserver.url]

    expected_id = job['_id']
    expected_name = job['name']

    db = pymongo.MongoClient("http://testurl").ophicleide

    db.models.insert_one(job)
    inq.put(job)

    p = Process(target=worker.workloop, args=("local[2]", inq, outq,
                                              "http://testurl"))
    p.start()

    # wait for worker to spin up
    outq.get()

    # wait for worker to train model, raise timeout if on a slower system.
    result = outq.get(timeout=15)
    p.terminate()
    mid = result[0]
    model_name = result[1]

    assert model_name == expected_name
    assert mid == expected_id
