from watson_developer_cloud import AlchemyLanguageV1
import boto3
import json

# Variables that contains the user credentials to access AlchemyAPI
alchemy_apikey = ""

class SQSSNSWorker():
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='tweet')
    alchemy_language = AlchemyLanguageV1(api_key=alchemy_apikey)

    def work(self):
        print 'working on tweets'
        while True:
            for message in self.queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=20):
                try:
                    data = json.loads(message.body)
                    tweet_text = data['text']
                    sentiment = self.alchemy_language.sentiment(text=tweet_text)
                    print 'text: ' + tweet_text
                    print 'sentiment: ' + sentiment['docSentiment']['type']
                    data['sentiment'] = sentiment['docSentiment']['type']
                    print data
                except Exception as e:
                    print e
                finally:
                    message.delete()

if __name__ == '__main__':
    worker = SQSSNSWorker()
    worker.work()
