from elasticsearch import Elasticsearch
from backoff_decorator import backoff



def connect_elasticsearch():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if not es.ping():
        raise ValueError("Connection failed")
    return es

connect_elasticsearch()
