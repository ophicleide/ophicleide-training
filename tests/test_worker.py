import pytest
import worker
from pyspark.mllib.feature import Word2VecModel
from pyspark.rdd import PipelinedRDD

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
