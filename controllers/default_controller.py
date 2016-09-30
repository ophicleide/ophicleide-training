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


def sanitize_model(m):
    result = dict([(k, m[k]) for k in ["_id", "name", "urls", "status"]])
    result["id"] = result.pop("_id")
    return result


def create_training_model(trainingModel) -> str:
    job = {"urls": trainingModel["urls"], "_id": uuid4(),
           "name": trainingModel["name"], "status": "training",
           "callback": trainingModel["callback"]}
    (model_collection()).insert_one(job)
    options()["train_queue"].put(job)
    location = url_for(".controllers_default_controller_find_training_model",
                  id=job["_id"])

    response = jsonify(sanitize_model(job))
    response.status_code = 201
    response.headers.add("Location", location)

    return response


def delete_training_model(id) -> str:
    model_collection().delete_one({"_id": UUID(id)})
    return("", 204)


def find_training_model(id) -> str:
    model = model_collection().find_one({"_id": UUID(id)})
    if model is None:
        return json_error("Not Found", 404, "can't find model with ID %r" % id, 404)
    else:
        return jsonify({'model' : sanitize_model(model)})


def get_training_models() -> str:
    models = model_collection().find()
    ms = [
        sanitize_model(m)
        for m in models
    ]
    ret = {'models': ms}
    return jsonify(ret)


def sanitize_query(q):
    result = dict([(k, v) for (k, v) in q.items()])
    result["id"] = result.pop("_id")

    if not "modelName" in result:
        result["modelName"] = "UNKNOWN"

    if not "model" in result:
        result["model"] = "UNKNOWN"

    return result


def json_error(title, status, details):
    error = { "title" : title, "status" : status, "details" : details }
    response = jsonify({ "errors" : [ error ] })
    response.status_code = status
    return response


def create_query(newQuery) -> str:
    mid = newQuery["model"]
    word = newQuery["word"]
    model = model_cache_find(mid)
    if model is None:
        msg = ("no trained model with ID %r available; " % mid) + \
              "check /models to see when one is ready"
        return json_error("Not Found", 404, msg)
    else:
        # XXX
        w2v = model["w2v"]
        qid = uuid4()
        try:
            syns = w2v.findSynonyms(word, 5)
            q = {
                "_id": qid, "word": word, "results": syns,
                 "modelName": model["name"], "model": mid
            }
            (query_collection()).insert_one(q)
            route = ".controllers_default_controller_find_query"
            location = url_for(route, id=str(qid))
            response = jsonify({'query': sanitize_query(q)})
            response.status_code = 201
            response.headers.add("Location", location)
            return response
        except KeyError:
            return json_error("Bad Request", 400, "'%s' isn't even in my vocabulary!" % word)


def find_query(id) -> str:
    q = query_collection().find_one({"_id": UUID(id)})
    return jsonify({'query': sanitize_query(q)})


def get_queries() -> str:
    queries = [sanitize_query(q) for q in query_collection().find()]
    ret = {'queries': queries}
    return jsonify(ret)


def get_server_info() -> str:
    tqlen = (options()["train_queue"]).qsize()
    info = {"training_queue_len": tqlen}
    return jsonify(name="ophicleide", version="0.0.0", info=info)
