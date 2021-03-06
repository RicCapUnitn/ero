import json
import warnings

import numpy

from eroproject.features import *


class PeopleFeaturesGenerator():
    '''Class to generate test features from probability distributions'''

    def __init__(self, person_features_path, comparable_featurs_path):
        comparable_features = json.load(open(comparable_featurs_path))
        self.sorted_comparable_features_names = sorted(
            comparable_features['features'])
        self.person_features = json.load(open(person_features_path))
        self.distributions = {}

    def generate_many(self, number_of_people):
        '''Generate multiple person features lists'''
        return [self.generate_one() for _ in range(number_of_people)]

    def generate_one(self):
        '''Generate one list of features'''

        features = []
        age = "15"
        for fname in self.sorted_comparable_features_names:

            try:
                ftype = self.person_features[fname]
            except KeyError:
                warnings.warn('Person feature not present: ' + feature)
                ftype = comparable_features.EMPTY_FEATURE

            try:
                fclass = self._get_comparable_feature_class_for_ftype(ftype)

                feature_distribution = self.distributions[fname]
                if fname == "age":
                    distribution_values = feature_distribution['values']
                    distribution_probabilities = feature_distribution['distribution']
                    distribution = numpy.random.choice(
                        distribution_values, p=distribution_probabilities)
                    age = str(distribution)
                else:
                    distribution_values = feature_distribution[age]['values']
                    distribution_probabilities = feature_distribution[age]['distribution']
                    distribution = numpy.random.choice(
                        distribution_values, p=distribution_probabilities)

                value = fclass(distribution)

            except NotImplementedError:
                warnings.warn('Feature type not defined: ' + str(ftype))
                value = empty_feature.empty_feature
            except KeyError:
                warnings.warn('Feature distribution not present: ' + fname)
                value = empty_feature.empty_feature

            features.append(value)

        return features

    def import_features_distributions_from_folder(self, folder_path):
        '''Import all features distributions from files'''

        for feature in self.person_features.keys():
            if isinstance(feature, unicode):
                feature_distribution_file_path = folder_path + feature + '_distribution.json'
            else:
                continue

            try:
                self.distributions[feature] = json.load(
                    open(feature_distribution_file_path))
            except IOError:
                warnings.warn('Feature distribution not present: ' + feature)

    def _get_comparable_feature_class_for_ftype(self, ftype):
        '''Get ComparableFeature subclass for feature type'''

        if ftype == comparable_feature.EMPTY_FEATURE_TYPE:
            fclass = empty_feature.empty_feature
        if ftype == comparable_feature.BINARY_FEATURE_TYPE:
            fclass = binary_feature.BinaryFeature
        else:
            raise NotImplementedError
        return fclass
