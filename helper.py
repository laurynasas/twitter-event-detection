import math

import cluster
import entity as en
import event_detection as ed
import tweet as tw

'''
    This module contains all helper methods used in filtering and merging of the clusters. Writing and reading data.
'''


class Helper:
    '''
        This method takes a file and read tweets in clusters sorted by time
    '''

    @staticmethod
    def read_clusters_sorted_by_time(file_name, named_entities_file_name):
        tweets = []
        clusters = {}
        clusters_timeline = []
        named_entities = {}
        file_to_read = open(file_name, "r")

        file_entities = open(named_entities_file_name, 'r')

        for line in file_entities.readlines():
            data = line.split(",", 1)
            named_entities[data[0]] = data[1]

        for line in file_to_read.readlines():
            data = line.split(",")
            tokens = [
                en.SimpleEntity(entity) if not (entity in named_entities.get(data[2])) else en.NamedEntity(
                    entity)
                for entity in data[5].split(" ")]
            tweet = tw.Tweet(clst_id=data[0], id=data[2], timestamp_ms=data[3], user_id=data[4],
                             tokens=tokens, content=data[6])
            tweets.append(tweet)
            if not clusters.get(data[0]):
                new_cl = cluster.Cluster(clst_id=data[0], clst_name=data[1], created_time=data[3])
                clusters[data[0]] = new_cl
                oldest_valid_time = new_cl.get_created_time() - ed.Constants.EPOCH * 8
                for past_cluster in clusters_timeline[::-1]:
                    if past_cluster.get_created_time() >= oldest_valid_time:
                        new_cl.add_past_neighbour(past_cluster)
                    else:
                        break
                clusters_timeline.append(new_cl)

            clusters[data[0]].append(tweet)

        for clst_id in clusters:
            clusters[clst_id].aggregate_entities()
        return tweets, clusters

    '''
        Opens a file and writes tweet id with their cluster label.
    '''

    @staticmethod
    def write_clusters_to_file(file_name, clusters):
        w_file = open("data/coursework/7days/" + file_name, "w")
        with w_file:
            for tweet_id in clusters:
                w_file.write(str(clusters[tweet_id]) + "," + str(tweet_id) + "\n")

    '''
        If two clusters contain enough same entities they are being merged
    '''

    @staticmethod
    def merge_two_clusuters(clst_a, clst_b, thr):
        inter = set(clst_a.get_entity_names()).intersection(clst_b.get_entity_names())

        clst_a_ent = clst_a.get_entities()
        clst_b_ent = clst_b.get_entities()

        if len(inter) * 1.0 / len(clst_a_ent) >= thr or len(inter) * 1.0 / len(clst_b_ent) >= thr:
            if len(clst_a_ent) >= len(clst_b_ent):
                for tweet in clst_b.get_tweets():
                    tweet.clst_id = clst_a.get_id()
                    clst_a.append(tweet)
                for entity in clst_b_ent:
                    clst_a.append_entity(entity)
                return clst_b.get_id()
            else:
                for tweet in clst_a.get_tweets():
                    tweet.clst_id = clst_b.get_id()
                    clst_b.append(tweet)
                for entity in clst_a_ent:
                    clst_b.append_entity(entity)
                return clst_a.get_id()
        else:
            return

    '''
        Analyses named entities in a clusters and estimates the entropy of a cluster
    '''

    @staticmethod
    def calculate_avg_cluster_entropy(cluster):

        named_entities = [named_ent.get_entity_name() for named_ent in cluster.get_named_entities()]

        entropy = 0
        N = len(named_entities)
        for name_entity in named_entities:
            n_i = named_entities.count(name_entity)
            entropy += (-1) * (n_i * 1.0 / N) * math.log(n_i * 1.0 / N)
        return entropy

    '''
        Only returns clusters that pass minimum number of tweets and minimum amount of named entities
    '''

    @staticmethod
    def do_cluster_filtering_tweets_and_named_entities(clusters, min_tweets, min_named_entities):
        filtered_cl = {}
        for clst_id in clusters:
            if len(clusters[clst_id].get_tweets()) >= min_tweets and len(
                    clusters[clst_id].get_named_entities()) >= min_named_entities:
                filtered_cl[clst_id] = clusters[clst_id]
        return filtered_cl

    @staticmethod
    def prepare_clusters_for_writing(clusters):
        labeled_tweets = {}
        for clst_id in clusters:
            for tweet in clusters[clst_id].get_tweets():
                labeled_tweets[tweet.get_id()] = clst_id

        return labeled_tweets

    '''
        Iterates through every cluster's neighbours and tries to merge them.
    '''

    @staticmethod
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

    '''
        Only pass clusters with certain entropy
    '''

    @staticmethod
    def do_entropy_filtering(clusters, min_entropy, helper):
        result_clusters = {}

        for clst_id in clusters:
            clusters[clst_id].entropy = helper.calculate_avg_cluster_entropy(clusters[clst_id])
            if clusters[clst_id].entropy >= min_entropy:
                result_clusters[clst_id] = clusters[clst_id]
        return result_clusters

    '''
        Only pass clusters that exceeds minimum gradient
    '''

    @staticmethod
    def do_gradient_filtering(clusters, min_grad):
        result_clusters = {}
        for clst_id in clusters:
            clusters[clst_id].calc_gradients()
            if any(grad >= min_grad for grad in clusters[clst_id].get_gradients()):
                result_clusters[clst_id] = clusters[clst_id]
        return result_clusters
