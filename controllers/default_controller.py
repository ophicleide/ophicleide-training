from uuid import uuid4

from flask import request, render_template, url_for, make_response
from flask.json import jsonify

from __main__ import options


def create_training_model(trainingModel) -> str:
    job = { "urls": trainingModel["urls"], "uuid": uuid4(),
            "name": trainingModel["name"] }
    options()["train_queue"].put(job)
    print(repr(trainingModel))
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
