import json

class DataReader:

    def read(self, filepath, keywords):
        data = {}
        for keyword in keywords:
            data[keyword] = []

        with open(filepath) as f:
            tweet_lines = f.readlines()
            for i in range(0, len(tweet_lines)):
                tweet_line = tweet_lines[i]
                tweet_json = json.loads(tweet_line)
                for keyword in keywords:
                    if keyword in tweet_json['text'].lower():
                        data[keyword].append(tweet_json)
        return data
