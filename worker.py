from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.mllib.feature import Word2Vec

from urllib.request import urlopen


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


def workloop(master, inq, outq):
    sconf = SparkConf().setAppName("ophicleide-worker").setMaster(master)
    sc = SparkContext(conf=sconf)

    outq.put("ready")

    while True:
        req = inq.get()
        model = train(sc, req["urls"])
        outq.put(model)
