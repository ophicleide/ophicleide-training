#!/usr/bin/env python3

import connexion
from multiprocessing import Process, Queue

from worker import workloop


optionsDict = {}


def options():
    global optionsDict
    return optionsDict


if __name__ == '__main__':
    train_q = Queue()
    result_q = Queue()

    master = "local[*]"
    dburl = "mongodb://localhost"

    options()["spark_master"] = master
    options()["db_url"] = dburl
    options()["train_queue"] = train_q
    options()["result_queue"] = result_q

    p = Process(target=workloop, args=(master, train_q, result_q, dburl))
    p.start()

    # wait for worker to spin up
    result_q.get()

    app = connexion.App(__name__, specification_dir='./swagger/')
    app.add_api('swagger.yaml',
                arguments={'title':
                           'The REST API for the Ophicleide Word2Vec server'})
    app.run(port=8080)
