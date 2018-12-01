from __future__ import division

from numpy import random

from features import *


class Person():

    def __init__(self, features, do_mutation=False):
        self.best_fitness = 0.
        self.best_event = None
        self.features = features
        self.features_weights = [0.5] * len(features)
        self.do_mutation = do_mutation

    def reset(self):
        '''Reset parameters after propagation'''
        self.best_fitness = 0.
        self.best_event = None
        self.features_weights = [0.5] * len(self.features)

    def mutate_evaluate_and_select(self, event, event_distance=1):
        '''Evaluate the fitness of an event and select it if best option

        Params:
            event: the Event whose fitness we are computing
            event_distance: the distance factor used in the fitness computation

        Note: this method tries to mutate features weights to better match the
        person features to the event features
        '''
        weights = self.features_weights
        fitness = self.fitness(event, weights)

        if self.do_mutation:
            mutated_weights = self._get_mutated_weights()
            mutated_fitness = self.fitness(event, mutated_weights)

            if mutated_fitness > fitness:
                weights = mutated_weights
                fitness = mutated_fitness

        # Apply distance factor to fitness
        fitness /= 2 ** event_distance

        if fitness >= self.best_fitness:
            self.best_event = event
            self.best_fitness = fitness
            self.features_weights = weights
            selected = True
        else:
            selected = False
        return selected

    def fitness(self, event, weights=None):
        '''Computed as average of fitnesses weighted'''
        weights = self.features_weights if weights is None else weights
        result = 0.
        for person_feature, event_feature, weight in zip(self.features, event.features, weights):
            result += weight * person_feature.similar(event_feature)

        if self.do_mutation:
            normalization_factor = 1. + sum(weights)
        else:
            normalization_factor = len(self.features)

        result /= normalization_factor
        return result

    def set_features_weights(self, default_weight):
        '''Set all features weights to default_weight'''
        self.features_weights = [default_weight] * len(self.features)

    def _get_mutated_weights(self, mutation_rate=0.1):
        '''
        Params:
            mutation_rate: value in [0,1] that defines the mutation range
        '''
        mutated_weights = self.features_weights[:]

        mutation_index = random.randint(0, len(mutated_weights))
        mutating_weight = mutated_weights[mutation_index]

        action = random.choice(['augment_weight', 'deminish_weight'])

        if action == 'augment_weight':
            mutation_range = (1. - mutating_weight)
        else:
            mutation_range = - mutating_weight

        normalized_mutated_weight = mutating_weight + \
            mutation_rate * (mutation_range * random.random_sample())

        mutated_weights[mutation_index] = normalized_mutated_weight
        return mutated_weights
