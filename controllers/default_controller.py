from uuid import uuid4

from flask import request, render_template, url_for, make_response
from flask.json import jsonify

import pymongo

from __main__ import options

def model_collection():
    dburl = options()["db_url"]
    return pymongo.MongoClient(dburl).ophicleide.models


def create_training_model(trainingModel) -> str:
    job = { "urls": trainingModel["urls"], "_id": uuid4(),
            "name": trainingModel["name"], "status": "training" }
    (model_collection()).insert_one(job)
    options()["train_queue"].put(job)
    
    return jsonify(job)


def delete_training_model(id) -> str:
    return 'do some magic!'


def find_training_model(id) -> str:
    return 'do some magic!'


def get_training_models() -> str:
    return 'do some magic!'


def create_query(newQuery) -> str:
    return 'do some magic!'


def find_query(id) -> str:
    return 'do some magic!'


def get_queries() -> str:
    return 'do some magic!'


def get_server_info() -> str:
    tqlen = (options()["train_queue"]).qsize()
    info = {"training_queue_len": tqlen}
    return jsonify(name="ophicleide", version="0.0.0", info=info)
