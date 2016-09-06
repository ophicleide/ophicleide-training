from uuid import uuid4, UUID

from flask import request, render_template, url_for, make_response, redirect
from flask.json import jsonify

import pymongo
from bson.objectid import ObjectId

from numpy import ndarray
from numpy.linalg import norm
from pickle import loads as pls
import zlib

from __main__ import options

mc = {}

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
        model = model_collection().find_one({"_id": UUID(mid), "status": "ready"})
        if model is None:
            return None
        else:
            vecs = pls(zlib.decompress(model["zndvecs"]))
            norms = ndarray([norm(v) for v in vecs])
            
            cached = {"name": model["name"], "words": dict(zip(model["words"], range(len(model["words"])))), "indices": model["words"], "vecs": vecs, "norms": norms}
            mc[mid] = cached
            return cached
            

def create_training_model(trainingModel) -> str:
    job = { "urls": trainingModel["urls"], "_id": uuid4(),
            "name": trainingModel["name"], "status": "training",
            "callback": trainingModel["callback"] }
    (model_collection()).insert_one(job)
    options()["train_queue"].put(job)
    url = url_for(".controllers_default_controller_find_training_model", id=job["_id"])

    return(redirect(url))


def delete_training_model(id) -> str:
    model_collection().delete_one({"_id": UUID(id)})
    return(redirect(url_for(".controllers_default_controller_get_training_models")))


def find_training_model(id) -> str:
    model = model_collection().find_one({"_id": UUID(id)})
    if model is None:
        return make_response(("can't find model with ID %r" % id, 404, []))
    else:
        result = dict([(k,model[k]) for k in ["_id", "name", "urls", "status"]])
        return jsonify(result)


def get_training_models() -> str:
    models = model_collection().find()
    result = [dict([(k,m[k]) for k in ["_id", "name", "urls", "status"]]) for m in models]
    return jsonify(result)


def create_query(newQuery) -> str:
    mid = newQuery["model"]
    word = newQuery["word"]
    model = model_cache_find(mid)
    if model is None:
        return make_response(("no trained model with ID %r available; check /models to see when one is ready" % mid, 404, []))
    else:
        # XXX
        return 'XXX do some magic'


def find_query(id) -> str:
    return 'do some magic!'


def get_queries() -> str:
    return 'do some magic!'


def get_server_info() -> str:
    tqlen = (options()["train_queue"]).qsize()
    info = {"training_queue_len": tqlen}
    return jsonify(name="ophicleide", version="0.0.0", info=info)
