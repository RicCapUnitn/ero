from operator import add

from features import *


class Person():

    def __init__(self, features):
        self.features = features

    def fitness(self, event):
        return sum(f1.similar(f2) for f1, f2 in zip(self.features, event.features))
