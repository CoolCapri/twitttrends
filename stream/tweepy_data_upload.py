import tweepy
import json
import ConfigParser
import os
from elasticsearch import Elasticsearch


conf_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'conf', 'config.txt')
configParser = ConfigParser.RawConfigParser()
configParser.read(conf_file)

access_token = configParser.get('TWITTER', 'ACCESS_TOKEN')
access_token_secret = configParser.get('TWITTER', 'ACCESS_TOKEN_SECRET')
consumer_key = configParser.get('TWITTER', 'CONSUMER_KEY')
consumer_secret = configParser.get('TWITTER', 'CONSUMER_SECRET')

es_host = configParser.get('ES', 'HOST')
es_port = configParser.get('ES', 'PORT')

class DataUploadStreamListener(tweepy.StreamListener):
    def __init__(self, es_host, es_port):
        super(DataUploadStreamListener, self).__init__()
        self.es = Elasticsearch([{'host': es_host, 'port': es_port}])

    def on_status(self, status):
        try:
            self.process(status._json)
        except KeyError as e:
            print ("KeyError: ", e)

    def on_error(self, status_code, data):
        print ("Error: ", status_code, ": ", data)

        # Want to stop trying to get data because of the error?
        # Uncomment the next line!
        if status_code == 420: # Rate limited!
            return False

    def process(self, data):
        keywords = ["music", "food", "sport", "show", "movie", "car", "commercial", "party", "war", "hello"]
        content = data['text'].lower()
        print("+++++")
        if any(x in content for x in keywords):
            if (data['coordinates'] is not None) and (data['lang']=='en'): # data[coordinates] may be null, want to filter it out
                print("------")
                print(data['text'])
                print(data['coordinates'])
                print(data['created_at'])
                print(data['timestamp_ms'])
                print(data['created_at'])
                print(data['user']['name'])
                print(data['user']['screen_name'])
                print("------")
                tweet_dict = {'text': data['text'],
                             'coordinates': data['coordinates']['coordinates'],
                             'created_at': data['created_at'],
                             'timestamp_ms': data['timestamp_ms'],
                             'user_name': data['user']['name'],
                             'user_screen_name': data['user']['screen_name']}
                self.es.index(index='tweet', doc_type='tweet_data', body=json.loads(json.dumps(tweet_dict)))


if __name__ == '__main__':
    duStreamListener = DataUploadStreamListener(es_host, es_port)
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    duStream = tweepy.Stream(auth, duStreamListener)
    keywords = ["music", "food", "sport", "show", "movie", "car", "commercial", "party", "war", "hello"]
    locations = [-180,-90,180,90]
    duStream.filter(track=keywords, locations=locations)
