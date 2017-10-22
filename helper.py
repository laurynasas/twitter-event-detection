import math

import event_detection as ed


class Helper:
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
            tokens = [ed.SimpleEntity(entity) if not (entity in named_entities.get(data[2])) else ed.NamedEntity(entity)
                      for entity in data[5].split(" ")]
            tweet = ed.Tweet(clst_id=data[0], id=data[2], timestamp_ms=data[3], user_id=data[4],
                             tokens=tokens, content=data[6])
            tweets.append(tweet)
            if not clusters.get(data[0]):
                new_cl = ed.Cluster(clst_id=data[0], clst_name=data[1], created_time=data[3])
                clusters[data[0]] = new_cl
                oldest_valid_time = new_cl.get_created_time() - ed.Constants.EPOCH*8
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

    @staticmethod
    def write_clusters_to_file(file_name, clusters):
        w_file = open("data/coursework/7days/" + file_name, "w")
        with w_file:
            for tweet_id in clusters:
                w_file.write(str(clusters[tweet_id]) + "," + str(tweet_id) + "\n")

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

    @staticmethod
    def calculate_avg_cluster_entropy(cluster):

        named_entities = [named_ent.get_entity_name() for named_ent in cluster.get_named_entities()]

        entropy = 0
        N = len(named_entities)
        for name_entity in named_entities:
            n_i = named_entities.count(name_entity)
            entropy += (-1) * (n_i * 1.0 / N) * math.log(n_i * 1.0 / N)
        return entropy
