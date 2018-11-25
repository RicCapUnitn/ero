from operator import add

from features import *


class Event():

    def __init__(self, event_id, features):
        self.id = int(str(event_id)[:5])	# The event ids from facebook are long numeric strings, we need ints...
        self.features = features
        self.relevance = 0

    def __lt__(self, other):
        return self.relevance < other.relevance
