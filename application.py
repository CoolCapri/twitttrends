from flask import Flask, jsonify, render_template, send_file, request, Response
from util.read_data import DataReader
from es.esearch import ESearch
import json
import requests
import time


# Set up the application
# EB looks for an 'application' callable by default.
application = Flask(__name__)

# pre-load fixed tweets
def pre_load_fixed_data():
    keywords = ["music", "food", "sport", "show", "movie", "car", "commercial", "party", "war", "hello"]
    data = DataReader()
    return data.read("static/data/tweets.txt", keywords)

tweets_json = pre_load_fixed_data()
esearch = ESearch()

new_tweets = []

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/search/')
@application.route('/search/<keyword>')
def search(keyword=None):
    if keyword is None:
        tweets_of_keyword = {"all": []}
        to_return = jsonify(**tweets_of_keyword)
    else:
        search_result = esearch.search(keyword)
        to_return = jsonify(**search_result)
    return to_return



@application.route('/addtweet', methods = ['GET', 'POST', 'PUT'])
def add_tweet():
    header = request.headers.get('x-amz-sns-message-type')
    try:
        data = json.loads(request.data)
    except:
        pass
    if header == 'SubscriptionConfirmation' and 'SubscribeURL' in data:
        url = data['SubscribeURL']
        response = requests.get(url)
        print "Subscribed to SNS: " + url
        return "Subscribed to SNS: " + url
    if header == 'Notification':
        print data['Message']
        search_result = esearch.upload(data['Message'])
        new_tweets.append(data['Message'])
        return data['Message']
    return "ok"


@application.route('/searchf/')
@application.route('/searchf/<keyword>')
def searchf(keyword=None):
    if keyword is None:
        to_return = jsonify(**tweets_json)
    else:
        tweets_of_keyword = {keyword: []}
        if keyword in tweets_json:
            tweets_of_keyword = {keyword: tweets_json[keyword]}
        to_return = jsonify(**tweets_of_keyword)
    return to_return

@application.route('/images/<filename>')
def get_image(filename=None):
    return send_file('static/img/'+filename, mimetype='image/png')

@application.route('/newtweetupdate/', methods=['GET', 'POST'])
def new_tweet_update():
    def respgen():
        while True:
            if len(new_tweets) > 0:
                new_tweet = new_tweets.pop(0)
                yield "data: " + new_tweet + "\n\n"
                print "yielded: " + new_tweet
            else:
                yield "data: nothing\n\n"
                print "yielded: nothing"
            time.sleep(0.5)

    return Response(respgen(), mimetype="text/event-stream")

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    #application.debug = True
    application.run(threaded=True)
