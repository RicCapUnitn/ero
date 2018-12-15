import comparable_feature


class CompositeFeature(comparable_feature.ComparableFeature):
    '''A feature that has a multidimensional representation'''

    def __init__(self, composite_value, combiner):
        '''
        Args:
            composite_value: an object(dict) readable by the combiner'''
        self.value = composite_value
        self.combiner = combiner

    def _similar(self, composite_feature):
        return self.combiner(self.value, composite_feature.value)
