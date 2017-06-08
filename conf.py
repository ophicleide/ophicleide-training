"""All project-wide global configs"""

optionsDict = {}


def options():
    global optionsDict
    return optionsDict


def init(master, dburl, train_q, result_q):
    options()["spark_master"] = master
    options()["db_url"] = dburl
    options()["train_queue"] = train_q
    options()["result_queue"] = result_q

