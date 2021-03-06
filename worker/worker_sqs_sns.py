from watson_developer_cloud import AlchemyLanguageV1
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
import boto3
import json
import ConfigParser
import os

conf_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'conf', 'config.txt')
configParser = ConfigParser.RawConfigParser()
configParser.read(conf_file)
alchemy_api_key = configParser.get('ALCHEMY', 'API_KEY')

class SQSSNSWorkerPool:
    def __init__(self, num_threads=2):
        sqs = boto3.resource('sqs')
        self.queue = sqs.get_queue_by_name(QueueName='tweet')
        self.alchemy_language = AlchemyLanguageV1(api_key=alchemy_api_key)
        sns_client = boto3.client('sns')
        topic_arn = sns_client.create_topic( Name='tweet')
        sns = boto3.resource('sns')
        self.topic = sns.Topic(topic_arn['TopicArn'])
        self.pool = ThreadPool(num_threads)

    def start(self):
        while True:
            messages = self.queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=20)
            print "Retrieved " + str(len(messages)) + " messages from sqs"
            self.pool.map(self.work, messages)

    def work(self, message):
        try:
            print "Worker: " + str(multiprocessing.dummy.current_process())
            data = json.loads(message.body)
            tweet_text = data['text']
            sentiment = self.alchemy_language.sentiment(text=tweet_text)
            data['sentiment'] = sentiment['docSentiment']['type']
            print data['sentiment']
            self.topic.publish(Message=json.dumps(data))
        except Exception as e:
            print e
        finally:
            message.delete()

if __name__ == '__main__':
    workerPool = SQSSNSWorkerPool()
    workerPool.start()
