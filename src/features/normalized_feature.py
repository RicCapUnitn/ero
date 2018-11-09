import comparable_feature
from combiners import *


class NormalizedFeature(comparable_feature.ComparableFeature):
    '''Normalized values are float in [0.,1.]'''

    def __init__(self, value, combiner=combiners.DEFAULT_NORMALIZED_COMBINER):
        '''
        Args:
            value: value in [0.,1.]
            comparison_function: function used to compute similarity between
            features; mind that each feature is compared differently
        '''
        self.combiner = combiner
        if value >= 0. and value <= 1.:
            self.value = float(value)

    def _similar(self, normalized_feature):
        return self.combiner(self.value, normalized_feature.value)
