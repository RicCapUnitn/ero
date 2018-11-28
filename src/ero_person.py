from __future__ import division

from features import *


class Person():

    def __init__(self, features):
        self.best_fitness = 0.
        self.best_event = None
        self.features = features
        self.features_weights = [1] * len(features)

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
        '''Computed as average of fitnesses weighted'''
        result = 0.
        for person_feature, event_feature, weight in zip(self.features, event.features, self.features_weights):
            result += weight * person_feature.similar(event_feature)
        result /= len(self.features)
        return result
