import tweepy
import boto.sqs
from boto.sqs.message import Message
import json

#Variables that contains the user credentials to access Twitter API
access_token = "Fill in Access Token"
access_token_secret = "Fill in Access Secret"
consumer_key = "Fill in Consumer Key"
consumer_secret = "Fill in Consumer Secret"

class SQSStreamListener(tweepy.StreamListener):
    conn = boto.sqs.connect_to_region("us-west-2", aws_access_key_id="some_access_key_id", aws_secret_access_key="some_ecret_access_key")
    # create_queue is actually get_or_create
    tweet_queue = conn.create_queue('tweet')
    keywords = ["music", "food", "sport", "show", "movie", "car", "commercial", "party", "war", "hello"]

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
            if (data['coordinates'] is not None) and (('lang' not in data) or (data['lang']=='en')): # data[coordinates] may be null, want to filter it out
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
                tweet_json = json.loads(json.dumps(tweet_dict))
                m = Message()
                m.set_body(tweet_json)
                self.tweet_queue.write(m)


if __name__ == '__main__':
    sqsStreamListener = SQSStreamListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    sqsStream = tweepy.Stream(auth, sqsStreamListener)
    keywords = ["music", "food", "sport", "show", "movie", "car", "commercial", "party", "war", "hello"]
    locations = [-180,-90,180,90]
    sqsStream.filter(track=keywords, locations=locations)
