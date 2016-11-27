# TwittTrends
Shuo Wang & Jisong Liu

### Note

Deployed on Elastic Beanstalk, built on Flask web framework. Tweets are streamed using Twitter Streaming API via Tweepy. Other technologies include: SQS, SNS, Server-Sent Event (SSE), EC2, etc.

Select keywords from keyword list or type a word to search. Markers of different colors indicate different sentiment (Red: positive, Green: negative, Yellow: neutral).

Markers are shown for each tweet. They are clustered when zoomed out.

User can click on markers to see details of tweets.

stream/tweepy_sqs.py file get tweets using Twitter Stream API and send it to SQS.

worker/worker_sqs_sns.py get tweets from SQS, does sentiment analysis, and then send tweets with sentiment information to SNS

application.py has add_tweet route which add tweet sent by SNS to ElasticSearch system

Web frontend will be notified of new tweets and display the new tweets to the map (live update of tweets).
