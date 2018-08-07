class User:

    def __init__(self, user_id, original_utterance):
        self.user_id = user_id
        self.original_utterance = original_utterance
        self.is_new = True
        self.login = None
        self.password = None
        self.servers = []
