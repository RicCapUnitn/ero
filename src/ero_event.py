from operator import add

from features import *


class Event():

    def __init__(self, event_id, features):
        self.id = event_id
        self.features = features
        self.relevance = 0

    def __lt__(self, other):
        return self.relevance < other.relevance

    def reset(self):
        '''Reset parameters after propagation'''
        self.relevance = 0
