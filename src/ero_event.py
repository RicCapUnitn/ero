from operator import add

from features import *


class Event():

    def __init__(self, features, event_id):
        self.features = features
        self.event_id = int(event_id[:5])	# The event ids from facebook are long numeric strings, we need ints...
