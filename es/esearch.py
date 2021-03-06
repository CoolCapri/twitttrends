from elasticsearch import Elasticsearch
import json
import requests

import ConfigParser
import os


class ESearch():
    def __init__(self):
        conf_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'conf', 'config.txt')
        configParser = ConfigParser.RawConfigParser()
        configParser.read(conf_file)
        es_host = configParser.get('ES', 'HOST')
        es_port = configParser.get('ES', 'PORT')
        self.es = Elasticsearch([{'host': es_host, 'port': es_port}])

    def search(self, keyword):
        es_data = self.es.search(index="tweet", size=2000, body={"query": {"match": {'text':{'query': keyword}}}})
        es_results = es_data['hits']['hits']
        tweets = []
        for es_result in es_results:
            tweets.append(es_result["_source"])
        tweets_of_keyword = {keyword: tweets}
        return tweets_of_keyword

    def upload(self, data_json):
        print data_json
        self.es.index(index='tweet', doc_type='tweet_data', body=json.loads(data_json))
