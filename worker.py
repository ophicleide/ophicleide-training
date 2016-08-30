from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.mllib.feature import Word2Vec

import re

from urllib.request import urlopen

from functools import reduce

import pymongo

def cleanstr(s):
    noPunct = re.sub("[^a-z ]", " ", s.lower())
    collapsedWhitespace = re.sub("(^ )|( $)", "", re.sub("  *", " ", noPunct))
    return collapsedWhitespace


def url2rdd(sc, url):
    response = urlopen(url)
    corpus_bytes = response.read()
    text = str(corpus_bytes).replace("\\r", "\r").replace("\\n", "\n")
    rdd = sc.parallelize(text.split("\r\n\r\n"))
    rdd.map(lambda l: l.replace("\r\n", " ").split(" "))
    return rdd.map(lambda l: cleanstr(l).split(" "))


def train(sc, urls):
    w2v = Word2Vec()
    rdds = reduce(lambda a, b: a.union(b), [url2rdd(sc, url) for url in urls])
    return w2v.fit(rdds)


def workloop(master, inq, outq, dburl):
    sconf = SparkConf().setAppName("ophicleide-worker").setMaster(master)
    sc = SparkContext(conf=sconf)

    if dburl is not None:
        db = pymongo.MongoClient(dburl).ophicleide

    outq.put("ready")

    while True:
        req = inq.get()
        urls = req["urls"]
        name = req["name"]
        mid = req["uuid"]
        model = train(sc, urls)

        if dburl is not None:
            db.models.insert_one({"model": model.getVectors(), "uuid": mid,
                                  "name": name, "urls": urls})
        outq.put((mid, name, model))
