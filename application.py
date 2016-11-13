from flask import Flask
from flask import jsonify
from flask import render_template
from flask import send_file

from util.read_data import DataReader
from es.esearch import ESearch

# Set up the application
# EB looks for an 'application' callable by default.
application = Flask(__name__, instance_relative_config=True)
# Load default configuration from config.py
application.config.from_object('config')
# Load custom configuration (e.g. creds) from instance/config.py
application.config.from_pyfile('config.py')

# pre-load fixed tweets
def pre_load_fixed_data():
    keywords = ["music", "food", "sport", "show", "movie", "car", "commercial", "party", "war", "hello"]
    data = DataReader()
    return data.read("static/data/tweets.txt", keywords)

tweets_json = pre_load_fixed_data()
esearch = ESearch()

@application.route('/')
def index():
    return render_template('index.html')

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

@application.route('/images/<filename>')
def get_image(filename=None):
    return send_file('static/img/'+filename, mimetype='image/png')

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.run()
