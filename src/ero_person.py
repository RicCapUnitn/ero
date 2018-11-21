from __future__ import division

from features import *


class Person():

    def __init__(self, features):
        self.features = features
        self.best_fitness = 0.
        self.best_event = None

    def evaluate_and_select(self, event):
        '''Evaluate the fitness of an event and select it if best option'''
        fitness = self.fitness(event)
        if fitness >= self.best_fitness:
            self.best_event = event
            self.best_fitness = fitness
            selected = True
        else:
            selected = False
        return selected

    def fitness(self, event):
        '''Computed as average of fitnesses'''
        return sum(f1.similar(f2)
                   for f1, f2 in zip(self.features, event.features)) / len(self.features)
