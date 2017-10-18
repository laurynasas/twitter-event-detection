import event_detection as ed


class Helper:
    @staticmethod
    def read_clusters_sorted_by_time(file_name):
        tweets = []
        clusters = {}
        file_to_read = open(file_name, "r")
        for line in file_to_read.readlines():
            data = line.split(",")
            tweet = ed.Tweet(clst_id=data[0], id=data[2], timestamp_ms=data[3], user_id=data[4],
                             tokens=data[5].split(" "), content=data[6])
            tweets.append(tweet)
            if not clusters.get(data[0]):
                clusters[data[0]] = ed.Cluster(clst_id=data[0], clst_name=data[1], created_time=data[3])
            clusters[data[0]].append(tweet)
        return tweets, clusters
