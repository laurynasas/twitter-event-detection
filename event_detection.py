import copy
import subprocess
from abc import ABCMeta, abstractmethod
from operator import attrgetter
import sys
import helper


class DataFiles:
    CLUSTERS_SORTED_BY_TIME = 'data/coursework/7days/clusters.sortedby.time.csv'
    NAMED_ENTITIES = 'data/coursework/7days/namedentities.sortedby.time.csv'


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

    def calc_gradients(self):
        self.__tweets.sort(key=attrgetter('timestamp'))
        for start in range(self.created_time, self.created_time + Constants.EVENT_PERIOD, Constants.EPOCH):
            dy = self.number_tweets_in_time_period(start, start + Constants.EPOCH)
            dx = Constants.EPOCH / 60 / 1000
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

    def aggregate_entities(self):
        for tweet in self.get_tweets():
            # print tweet
            for entity in tweet.get_entities():
                self.append_entity(entity)

    def add_past_neighbour(self, neighbour):
        self.neigh.append(neighbour)

    def get_past_neighbours(self):
        return self.neigh

    def get_named_entities(self):
        named_entities = []
        for entity in self.get_entities():
            if isinstance(entity, NamedEntity):
                named_entities.append(entity)
        return named_entities


class Entity:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_entity_name(self):
        pass


class NamedEntity(Entity):
    def __init__(self, named_entity):
        self.entity = named_entity

    def get_entity_name(self):
        return self.entity


class SimpleEntity(Entity):
    def __init__(self, simple_entity):
        self.entity = simple_entity

    def get_entity_name(self):
        return self.entity


class Tweet:
    def __init__(self, id, content, clst_id, timestamp_ms, user_id, tokens):
        self.id = id
        self.tokens = tokens
        self.clst_id = clst_id
        self.timestamp = long(timestamp_ms)
        self.content = content
        self.user_id = user_id
        self.tokens = tokens

    def add_token(self, token):
        self.tokens.append(token)

    def get_timestamp(self):
        return self.timestamp

    def get_id(self):
        return self.id

    def __str__(self):
        return self.id + " " + str(self.timestamp) + " " + self.clst_id + " " + self.content + " | " + str(
            len(self.tokens))

    def get_entities(self):
        return self.tokens


class Constants:
    MERGING_THR = 1.0
    MERGING_ITER = 1

    MIN_TWEETS = 14

    MIN_GRADIENT = 0.1

    ENTROPY_THR = 5.0

    NAMED_ENTITIES_THR = 20
    EPOCH = 5 * 60 * 1000  # 20 mins in ms
    EVENT_PERIOD = 180 * 60 * 1000  # 2 hrs in ms

    PARAMS = {
        "trials": 21,
        "merging_thr": [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3,  0.2, 0.15, 0.25, 0.1, 0.35, 0.4, 0.45,  0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
        "merging_iter": [1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1,  1, 1, 1, 1, 1, 1, 1],
        "min_tweets": [9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9,  9, 9, 9, 9, 9, 9, 9],
        "min_gradient": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  0.1, 0.2, 0.3, 0.4, 0.6, 1.0, 2.0],
        "entropy_thr": [1, 2, 3, 4, 5, 6, 7,  1, 2, 3, 4, 5, 6, 7,  1, 2, 3, 4, 5, 6, 7],
        "named_entities": [11, 11, 11, 11, 11, 11, 11,  11, 11, 11, 11, 11, 11, 11,  11, 11, 11, 11, 11, 11, 11]
    }


def do_cluster_filtering_tweets_and_named_entities(clusters, min_tweets, min_named_entities):
    filtered_cl = {}
    for clst_id in clusters:
        if len(clusters[clst_id].get_tweets()) >= min_tweets and len(
                clusters[clst_id].get_named_entities()) >= min_named_entities:
            filtered_cl[clst_id] = clusters[clst_id]
    return filtered_cl


def do_cluster_merging(clusters, max_iter, merging_thr, helper):
    merged_clusters = {}
    for i in range(max_iter):
        for clst_id in clusters:
            if not clusters[clst_id]:
                continue
            for neigh in clusters[clst_id].get_past_neighbours():
                if not clusters[clst_id]:
                    break
                if not clusters.get(neigh.get_id()):
                    continue

                to_delete_clst_id = helper.merge_two_clusuters(clusters[clst_id], neigh, merging_thr)

                if to_delete_clst_id:
                    clusters[to_delete_clst_id] = None

    for clst_id in clusters:
        if clusters[clst_id]:
            merged_clusters[clst_id] = clusters[clst_id]

    return merged_clusters


def do_entropy_filtering(clusters, min_entropy, helper):
    result_clusters = {}

    for clst_id in clusters:
        clusters[clst_id].entropy = helper.calculate_avg_cluster_entropy(clusters[clst_id])
        if clusters[clst_id].entropy >= min_entropy:
            result_clusters[clst_id] = clusters[clst_id]
    return result_clusters


def do_gradient_filtering(clusters, min_grad):
    result_clusters = {}
    for clst_id in clusters:
        clusters[clst_id].calc_gradients()
        if any(grad >= min_grad for grad in clusters[clst_id].get_gradients()):
            result_clusters[clst_id] = clusters[clst_id]
    return result_clusters


def prepare_clusters_for_writing(clusters):
    labeled_tweets = {}
    for clst_id in clusters:
        for tweet in clusters[clst_id].get_tweets():
            labeled_tweets[tweet.get_id()] = clst_id

    return labeled_tweets


if __name__ == "__main__":
    helper = helper.Helper()
    number_trials = Constants.PARAMS["trials"]
    sys.setrecursionlimit(10000)
    init_tweets, init_clusters = helper.read_clusters_sorted_by_time(DataFiles.CLUSTERS_SORTED_BY_TIME,
                                                                     DataFiles.NAMED_ENTITIES)
    for i in range(number_trials):
        print i
        min_tweets = Constants.PARAMS["min_tweets"][i]
        named_ent_thr = Constants.PARAMS["named_entities"][i]
        merging_iter = Constants.PARAMS["merging_iter"][i]
        merging_thr = Constants.PARAMS["merging_thr"][i]
        entropy_thr = Constants.PARAMS["entropy_thr"][i]
        gradient_thr = Constants.PARAMS["min_gradient"][i]

        out_file = "twitter_id.clst_id.over_9_tweets.csv"
        log = open('log.txt', 'a')

        log.write("\n")
        log.write("\t\t=========== TRIAL " + str(i) + " ============\n")
        log.write("PARAMS: \n")
        log.write("min_tweets:".ljust(20) + str(min_tweets) + "\n")
        log.write("named_entities:".ljust(20) + str(named_ent_thr) + "\n")
        log.write("merging_iter:".ljust(20) + str(merging_iter) + "\n")
        log.write("merging_thr:".ljust(20) + str(merging_thr) + "\n")
        log.write("entropy_thr:".ljust(20) + str(entropy_thr) + "\n")
        log.write("min_gradient:".ljust(20) + str(gradient_thr) + "\n")
        log.write("event_period (min):".ljust(20) + str(Constants.EVENT_PERIOD / 60 / 1000) + "\n")
        log.write("min_epoch (min):".ljust(20) + str(Constants.EPOCH / 60 / 1000) + "\n")
        log.close()
        log = open('log.txt', 'a')

        clusters = copy.deepcopy(init_clusters)

        if not (min_tweets == 0 and named_ent_thr == 0):
            clusters = do_cluster_filtering_tweets_and_named_entities(clusters, min_tweets, named_ent_thr)

        if merging_thr != -1:
            clusters = do_cluster_merging(clusters, merging_iter, merging_thr, helper)

        if entropy_thr != 0:
            clusters = do_entropy_filtering(clusters, entropy_thr, helper)

        if gradient_thr != 0:
            clusters = do_gradient_filtering(clusters, gradient_thr)

        labeled_tweets = prepare_clusters_for_writing(clusters)

        helper.write_clusters_to_file(out_file, labeled_tweets)

        subprocess.call("python eval.py ../7days/" + out_file, shell=True, cwd="data/coursework/eval/", stdout=log)
        log.write("==================================================================================\n")
        log.close()
