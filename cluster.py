from operator import attrgetter

from entity import NamedEntity
from event_detection import Constants

'''
    A class to hold structure for Cluster instance and auxiliary cluster methods
'''


class Cluster:
    def __init__(self, clst_id, clst_name, created_time):
        self.__gradients = []
        self.id = clst_id
        self.name = clst_name
        self.__tweets = []
        self.created_time = long(created_time)
        self.__entities = []
        self.entity_names = []
        self.neigh = []
        self.entropy = None

    '''
        Calculates how many tweets in a certain time period
        were tweeted for this particular clusters
    '''

    def number_tweets_in_time_period(self, start_time, end_time):
        count = 0
        for tweet in self.__tweets:
            ts = tweet.get_timestamp()
            if ts >= start_time and ts < end_time:
                count += 1
                if ts >= end_time:
                    return count

        return count

    def get_created_time(self):
        return self.created_time

    def get_id(self):
        return self.id

    def append(self, tweet):
        self.__tweets.append(tweet)

    '''
        Gradient calculation, where event time window is divided into epochs. The gradient of the number of tweets per
        time chunk is calculated and appended to gradient list
    '''

    def calc_gradients(self):
        self.__tweets.sort(key=attrgetter('timestamp'))
        for start in range(self.created_time, self.created_time + Constants.EVENT_PERIOD, Constants.EPOCH):
            dy = self.number_tweets_in_time_period(start, start + Constants.EPOCH)
            dx = Constants.EPOCH / 60 / 1000  # EPOCH is in mins so we have to covert it to ms
            self.__gradients.append(dy * 1.0 / dx)

    def get_gradients(self):
        return self.__gradients

    def get_tweets(self):
        return self.__tweets

    def get_tweet_ids(self):
        return [tweet.get_id() for tweet in self.get_tweets()]

    def append_entity(self, entity):
        self.__entities.append(entity)
        self.entity_names.append(entity.get_entity_name())

    def get_entities(self):
        return self.__entities

    def get_entity_names(self):
        return self.entity_names

    '''
        Collects all entities from all tweets in a cluster
    '''

    def aggregate_entities(self):
        for tweet in self.get_tweets():
            for entity in tweet.get_entities():
                self.append_entity(entity)

    def add_past_neighbour(self, neighbour):
        self.neigh.append(neighbour)

    def get_past_neighbours(self):
        return self.neigh

    '''
        finds only named entities from all entities list
    '''

    def get_named_entities(self):
        named_entities = []
        for entity in self.get_entities():
            if isinstance(entity, NamedEntity):
                named_entities.append(entity)
        return named_entities
