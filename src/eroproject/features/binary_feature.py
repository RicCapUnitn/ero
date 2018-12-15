import comparable_feature


class BinaryFeature(comparable_feature.ComparableFeature):

    def __init__(self, binary_value):
        self.value = bool(binary_value)

    def _similar(self, binary_feature):
        return 1. if binary_feature.value == self.value else 0.
