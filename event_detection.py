from abc import ABCMeta, abstractmethod
from operator import attrgetter
from helper import Helper

class DataFiles:
    CLUSTERS_SORTED_BY_TIME = 'data/coursework/1day/clusters.sortedby.time.csv'

class Cluster:
    EPOCH = 5 * 60 * 1000  # 5 mins in ms
    EVENT_PERIOD = 120 * 60 * 1000  # 2 hrs in ms

    def __init__(self, clst_id, clst_name, created_time):
        self.gradients = []
        self.id = clst_id
        self.name = clst_name
        self.tweets = []
        self.created_time = created_time

    #
    # def binary_search(self, a, x, lo=0, hi=None):  # can't use a to specify default for hi
    #     hi = hi if hi is not None else len(a)  # hi defaults to len(a)
    #     pos = bisect_left(a, x, lo, hi)  # find insertion position
    #     return (pos if pos != hi and a[pos] == x else -1)  # don't walk off the end

    def number_tweets_in_time_period(self, start_time, end_time):
        count = 0
        for tweet in self.tweets:
            ts = tweet.get_timestamp()
            if ts >= start_time and ts < end_time:
                count += 1
                if ts >= end_time:
                    return count

        return count

    def get_gradients(self):
        self.tweets.sort(key=attrgetter('timestamp'))
        # start_tweet_pos = self.binary_search([tweet.get_timestamp() for tweet in self.tweets], self.created_time)

        for start in range(self.created_time, self.created_time + Cluster.EVENT_PERIOD, Cluster.EPOCH):
            dy = self.number_tweets_in_time_period(start, start + Cluster.EPOCH)
            dx = Cluster.EPOCH
            self.gradients.append(dy * 1.0 / dx)


class Entity:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_entity(self):
        pass


class NamedEntity(Entity):
    def __init__(self, named_entity):
        self.entity = named_entity

    def get_entity(self):
        return self.entity


class SimpleEntity(Entity):
    def __init__(self, simple_entity):
        self.entity = simple_entity

    def get_entity(self):
        return self.entity


class Tweet:
    def __init__(self, id, content, clst_id, timestamp_ms, user_id, tokens):
        self.id = id
        self.tokens = tokens
        self.clst_id = clst_id
        self.timestamp = timestamp_ms
        self.content = content
        self.user_id = user_id
        self.tokens = []

    def add_token(self, token):
        self.tokens.append(token)

    def get_timestamp(self):
        return self.timestamp


if __name__ == "__main__":
    helper = Helper()
    tweets = helper.read_clusters_sorted_by_time(DataFiles.CLUSTERS_SORTED_BY_TIME)

