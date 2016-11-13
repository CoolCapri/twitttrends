import tweepy
import boto3
import json

#Variables that contains the user credentials to access Twitter API
access_token = ""
access_token_secret = ""
consumer_key = ""
consumer_secret = ""

class SQSStreamListener(tweepy.StreamListener):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='tweet')
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
    keywords = ["music", "food", "sport", "show", "movie", "car", "commercial", "party", "war", "hello"]
    locations = [-180,-90,180,90]
    sqsStream.filter(track=keywords, locations=locations)
