import argparse

from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.mllib.feature import Word2Vec

import re
from urllib2 import urlopen

from multiprocessing import Process, Queue
import json


class TrainingRequest(object):
    def __init__(self, urls, callback, name):
        self.urls = urls
        self.callback = callback
        self.name = name

    def postup(model):
        vecs = model.getVectors()
        


def cleanstr(s):
    noPunct = re.sub("[^a-z ]", " ", s.lower())
    collapsedWhitespace = re.sub("(^ )|( $)", "", re.sub("  *", " ", noPunct))
    return collapsedWhitespace


def url2rdd(sc, url):
    response = urlopen(url)
    rdd = sc.parallelize(response.read().split("\r\n\r\n"))
    rdd.map(lambda l: l.replace("\r\n", " ").split(" "))
    return rdd.map(lambda l: cleanstr(l).split(" "))


def train(sc, urls):
    w2v = Word2Vec()
    rdds = reduce(lambda a, b: a.union(b), [url2rdd(sc, url) for url in urls])
    return w2v.fit(rdd)


def loop(sc, pollPeriod, q, endpoint):
    """ Event loop for thread interacting with REST service.  Checks 
    the REST server at endpoint to see if any training requests are
    available; if so, places one on the queue and checks
    again.  Sleeps for pollPeriod if no training requests are
    available. """
    pass


def trainingLoop(sc, q):
    """ Event loop for training thread; services queued TrainingRequests. """
    while True:
        tr = q.get()
        model = train(sc, tr.urls)
        

def main():
    pass
