'''
    This is a simple structure for a tweet
'''

class Tweet:
    def __init__(self, id, content, clst_id, timestamp_ms, user_id, tokens):
        self.id = id
        self.tokens = tokens
        self.clst_id = clst_id
        self.timestamp = long(timestamp_ms)
        self.content = content
        self.user_id = user_id
        self.tokens = tokens

    # By tokens we refer to entities
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