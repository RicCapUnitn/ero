from operator import add

from features import *


class Event():

    def __init__(self, event_id, features):
        self.id = event_id
        self.features = features[:]
        self.relevance = 0

    def __lt__(self, other):
        if self.relevance < other.relevance:
            return self.relevance < other.relevance
        elif self.relevance == other.relevance:
            return self.id < other.id
        else:
            return False

    def reset(self):
        '''Reset parameters after propagation'''
        self.relevance = 0
