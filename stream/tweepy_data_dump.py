import tweepy
import json

#Variables that contains the user credentials to access Twitter API
access_token = "Fill in Access Token"
access_token_secret = "Fill in Access Secret"
consumer_key = "Fill in Consumer Key"
consumer_secret = "Fill in Consumer Secret"


class MyStreamListener(tweepy.StreamListener):
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
                with open('tweets.txt', 'a') as outfile:
                    json.dump(tweet_dict, outfile)
                    outfile.write('\n')



if __name__ == '__main__':
    myStreamListener = MyStreamListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    myStream = tweepy.Stream(auth, myStreamListener)
    keywords = ["music", "food", "sport", "show", "movie", "car", "commercial", "party", "war", "hello"]
    locations = [-180,-90,180,90]
    myStream.filter(track=keywords, locations=locations)
