from flask import request, render_template, url_for, make_response
from flask.json import jsonify

from __main__ import options


def create_training_model(trainingModel) -> str:
    print(repr(trainingModel))
    return 'do some magic!'


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
