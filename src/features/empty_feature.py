import comparable_feature


class __EmptyFeature(comparable_feature.ComparableFeature):
    '''Empty feature is used when a feature is missing

    Do not instantiate this class. Use the empty_feature instance instead.
    '''

    def __init__(self):
        self.value = comparable_feature.EMPTY_FEATURE_TYPE

    def _similar(self, other):
        return 0


# Use only one instance
empty_feature = __EmptyFeature()
