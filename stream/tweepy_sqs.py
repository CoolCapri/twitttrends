import tweepy
import boto3
import json
import ConfigParser
import os


conf_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'conf', 'config.txt')
configParser = ConfigParser.RawConfigParser()
configParser.read(conf_file)

access_token = configParser.get('TWITTER', 'ACCESS_TOKEN')
access_token_secret = configParser.get('TWITTER', 'ACCESS_TOKEN_SECRET')
consumer_key = configParser.get('TWITTER', 'CONSUMER_KEY')
consumer_secret = configParser.get('TWITTER', 'CONSUMER_SECRET')

class SQSStreamListener(tweepy.StreamListener):
    keywords = ["music", "food", "sport", "show", "movie", "car", "commercial", "hello", "love", "like"]

    def __init__(self):
        super(SQSStreamListener, self).__init__()
        sqs = boto3.resource('sqs')
        self.queue = sqs.get_queue_by_name(QueueName='tweet')

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
        content = data['text'].lower()
        print("+++++")
        if any(x in content for x in self.keywords):
            if (data['coordinates'] is not None) and (data['lang'] == 'en'): # data[coordinates] may be null, want to filter it out
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
                tweet_json = json.dumps(tweet_dict)
                response = self.queue.send_message(MessageBody=tweet_json)


if __name__ == '__main__':
    sqsStreamListener = SQSStreamListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    sqsStream = tweepy.Stream(auth, sqsStreamListener)
    keywords = ["music", "food", "sport", "show", "movie", "car", "commercial", "hello", "love", "like"]
    locations = [-180,-90,180,90]
    sqsStream.filter(track=keywords, locations=locations)
