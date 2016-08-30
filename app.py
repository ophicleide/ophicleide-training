#!/usr/bin/env python3

import connexion
from multiprocessing import Process, Queue

optionsDict = {}

from worker import workloop

def options():
    global optionsDict
    return optionsDict

if __name__ == '__main__':
    train_queue = Queue()
    result_queue = Queue()
    
    options()["spark_master"] = "local[*]"
    
    options()["train_queue"] = train_queue
    options()["result_queue"] = result_queue

    p = Process(target=workloop, args=(master, train_queue, result_queue))
    p.start()
    
    # wait for worker to spin up
    result_queue.get()
    
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.add_api('swagger.yaml', arguments={'title': 'The REST API for the Ophicleide Word2Vec server'})
    app.run(port=8080)
