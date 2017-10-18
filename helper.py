from event_detection import Tweet, Cluster


class Helper:
    def read_clusters_sorted_by_time(self, file_name):
        tweets = []
        clusters = {}
        file_to_read = open(file_name, "r")
        for line in file_to_read.readlines():
            data = line.split(",")
            tweets.append(
                Tweet(clst_id=data[0], id=data[2], timestamp_ms=data[3], user_id=data[4], tokens=data[5].split(" "),
                      content=data[6]))
            if not clusters.get(data[0]):
                clusters[data[0]] = Cluster(clst_id=data[0], clst_name=data[1], created_time=data[3])
        return tweets, clusters
