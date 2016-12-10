from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.mllib.feature import Word2Vec

from functools import reduce
import re
import urllib2
import zlib

from numpy import ndarray
import pymongo
from bson.binary import Binary


def cleanstr(s):
    noPunct = re.sub("[^a-z ]", " ", s.lower())
    collapsedWhitespace = re.sub("(^ )|( $)", "", re.sub("  *", " ", noPunct))
    return collapsedWhitespace


def url2rdd(sc, url):
    response = urllib2.urlopen(url)
    corpus = response.read()
    text = corpus.replace("\\r", "\r").replace("\\n", "\n")
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
        job = inq.get()
        urls = job["urls"]
        mid = job["_id"]
        model = train(sc, urls)

        items = model.getVectors().items()
        words, vecs = zip(*[(w, list(v)) for w, v in items])

        # XXX: do something with callback here

        if dburl is not None:
            ndvecs = ndarray([len(words), len(vecs[0])])
            for i in range(len(vecs)):
                ndvecs[i] = vecs[i]

            ns = ndvecs.dumps()
            zns = zlib.compress(ns, 9)

            print("len(ns) == %d; len(zns) == %d" % (len(ns), len(zns)))

            db.models.update_one(
                {"_id": mid},
                {"$set": {"status": "ready",
                          "model": {"words": list(words), "zndvecs": Binary(zns)}},
                 "$currentDate": {"last_updated": True}}
            )

        outq.put((mid, job["name"]))
