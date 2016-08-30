from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.mllib.feature import Word2Vec

def workloop(master, inq, outq):
    sconf = SparkConf().setAppName("ophicleide-worker").setMaster(master)
    sc = SparkContext(conf=sconf)

    outq.put("ready")

    while True:
        req = inq.get
        
