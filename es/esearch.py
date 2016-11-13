from elasticsearch import Elasticsearch
import json
import requests

class ESearch():
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    def search(self, keyword):
        es_data = self.es.search(index="tweet", size=2000, body={"query": {"match": {'text':{'query': keyword}}}})
        es_results = es_data['hits']['hits']
        tweets = []
        for es_result in es_results:
            tweets.append(es_result["_source"])
        tweets_of_keyword = {keyword: tweets}
        return tweets_of_keyword
