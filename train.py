import argparse

from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.mllib.feature import Word2Vec

import re
from urllib2 import urlopen

def cleanstr(s):
    noPunctuation = re.sub("[^a-z ]", " ", s.lower())
    collapsedWhitespace = re.sub("(^ )|( $)", "", re.sub("  *", " ", noPunctuation))
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

def loop(sc, pollPeriod, endpoint):
    """ Event loop for training app.  Checks the REST server at endpoint
    to see if any training requests are available; if so, services
    one, returns a result, and checks again.  Sleeps for pollPeriod if
    no training requests are available. """
    pass

def main():
    pass
