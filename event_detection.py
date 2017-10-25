import copy
import subprocess
import sys

import helper


class DataFiles:
    CLUSTERS_SORTED_BY_TIME = 'data/coursework/7days/clusters.sortedby.time.csv'
    NAMED_ENTITIES = 'data/coursework/7days/namedentities.sortedby.time.csv'


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
        "trials": 1,
        "merging_thr": [1.0],
        "merging_iter": [1],
        "min_tweets": [9],
        "min_gradient": [0.0],
        "entropy_thr": [0],
        "named_entities": [11]
    }


'''
    This is the main method, where we apply all filters and merge clusters.
'''

if __name__ == "__main__":
    helper = helper.Helper()
    number_trials = Constants.PARAMS["trials"]
    sys.setrecursionlimit(10000)  # had to do that because neighbour calculation is too deeply nested for default value

    # returns a list for all tweets and a dict of initial clusters
    init_tweets, init_clusters = helper.read_clusters_sorted_by_time(DataFiles.CLUSTERS_SORTED_BY_TIME,
                                                                     DataFiles.NAMED_ENTITIES)

    # We iterate to perform event detection with different set of parameters in order to find highest
    # accuracy/recall and f-values
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

        # every time we test a new set of params we perfom filtering and merging on a fresk dict of initial clusters
        clusters = copy.deepcopy(init_clusters)

        print "Number of init clusters: ", len(init_clusters)

        # Discards clusters which do not have minimum number of tweets and minimum number of named entities
        if not (min_tweets == 0 and named_ent_thr == 0):
            clusters = helper.do_cluster_filtering_tweets_and_named_entities(clusters, min_tweets, named_ent_thr)
        print "Number of clust after initial filtering: ", len(clusters)

        # Clusters are being merged wth their neighbours
        if merging_thr != -1:
            clusters = helper.do_cluster_merging(clusters, merging_iter, merging_thr, helper)

        # We eliminate remaining clusters with little important information
        if entropy_thr != 0:
            clusters = helper.do_entropy_filtering(clusters, entropy_thr, helper)

        # We only select clusters which had activity bursts (potential event indicators)
        if gradient_thr != 0:
            clusters = helper.do_gradient_filtering(clusters, gradient_thr)

        labeled_tweets = helper.prepare_clusters_for_writing(clusters)

        helper.write_clusters_to_file(out_file, labeled_tweets)

        subprocess.call("python eval.py ../7days/" + out_file, shell=True, cwd="data/coursework/eval/", stdout=log)
        log.write("==================================================================================\n")
        log.close()
