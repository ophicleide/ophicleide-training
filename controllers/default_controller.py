from uuid import uuid4, UUID

from flask import request, render_template, url_for, make_response, redirect
from flask.json import jsonify

import pymongo
from bson.objectid import ObjectId

from numpy import ndarray, array, matmul
from numpy.linalg import norm
from pickle import loads as pls
import zlib

import heapq

from __main__ import options

mc = {}


class LocalW2VModel(object):
    def __init__(self, ws, vs):
        self.words = ws
        self.indices = dict(zip(ws, range(len(ws))))
        self.mat = vs
        self.norms = array([norm(v) for v in vs])

    def hasWord(self, word):
        return word in self.indices

    def findSynonyms(self, word_or_vec, count):
        if type(word_or_vec) is str:
            vec = self.mat[self.indices[word_or_vec]]
        else:
            vec = word_or_vec

        vnorm = norm(vec)
        if vnorm != 0.0:
            vec = vec * (1 / vnorm)

        simvec = (matmul(self.mat, vec) / self.norms)
        similarities = []

        for tup in zip(simvec, self.words):
            if len(similarities) < count + 1:
                heapq.heappush(similarities, tup)
            else:
                heapq.heappushpop(similarities, tup)

        return [(s, w)
                for s, w in heapq.nlargest(count + 1, similarities)
                if w != word_or_vec][:count]


def model_collection():
    dburl = options()["db_url"]
    return pymongo.MongoClient(dburl).ophicleide.models


def query_collection():
    dburl = options()["db_url"]
    return pymongo.MongoClient(dburl).ophicleide.queries


def model_cache_find(mid):
    global mc
    if mid in mc:
        return mc[mid]
    else:
        model = model_collection().find_one({"_id": UUID(mid),
                                             "status": "ready"})
        if model is None:
            return None
        else:
            m = model["model"]
            vecs = pls(zlib.decompress(m["zndvecs"]))
            w2v = LocalW2VModel(m["words"], vecs)
            cached = {"name": model["name"], "w2v": w2v}
            mc[mid] = cached
            return cached


def create_training_model(trainingModel) -> str:
    job = {"urls": trainingModel["urls"], "_id": uuid4(),
           "name": trainingModel["name"], "status": "training",
           "callback": trainingModel["callback"]}
    (model_collection()).insert_one(job)
    options()["train_queue"].put(job)
    url = url_for(".controllers_default_controller_find_training_model",
                  id=job["_id"])

    return(redirect(url))


def delete_training_model(id) -> str:
    model_collection().delete_one({"_id": UUID(id)})
    route = ".controllers_default_controller_get_training_models"
    return(redirect(url_for(route)))


def find_training_model(id) -> str:
    model = model_collection().find_one({"_id": UUID(id)})
    if model is None:
        return make_response(("can't find model with ID %r" % id, 404, []))
    else:
        m = dict([(k, model[k]) for k in ["_id", "name", "urls", "status"]])
        return jsonify(m)


def get_training_models() -> str:
    models = model_collection().find()
    ms = [
        dict([(k, m[k]) for k in ["_id", "name", "urls", "status"]])
        for m in models
    ]

    return jsonify(ms)


def create_query(newQuery) -> str:
    mid = newQuery["model"]
    word = newQuery["word"]
    model = model_cache_find(mid)
    if model is None:
        msg = ("no trained model with ID %r available; " % mid) + \
              "check /models to see when one is ready"
        return make_response((msg, 404, []))
    else:
        # XXX
        w2v = model["w2v"]
        qid = uuid4()
        syns = w2v.findSynonyms(word, 5)
        q = {"_id": qid, "word": word, "results": syns}
        (query_collection()).insert_one(q)
        route = ".controllers_default_controller_find_query"
        return redirect(url_for(route, id=str(qid)))


def find_query(id) -> str:
    result = query_collection().find_one({"_id": UUID(id)})
    return jsonify(result)


def get_queries() -> str:
    queries = [q for q in query_collection().find()]
    ret = {'queries': queries}
    return jsonify(ret)


def get_server_info() -> str:
    tqlen = (options()["train_queue"]).qsize()
    info = {"training_queue_len": tqlen}
    return jsonify(name="ophicleide", version="0.0.0", info=info)
