import comparable_feature


class NormalizedFeature(comparable_feature.ComparableFeature):
    '''Normalized values are float in [0.,1.]'''

    def __init__(self, value, comparison_function=comparable_feature.DEFAULT_NORMALIZED_COMPARISON):

        self.comparison_function = comparison_function
        if value >= 0. and value <= 1.:
            self.value = float(value)

    def _similar(self, normalized_feature):
        return self.comparison_function(self.value, normalized_feature.value)
