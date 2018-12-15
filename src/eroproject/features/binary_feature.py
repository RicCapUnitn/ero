from distutils.util import strtobool

import comparable_feature


class BinaryFeature(comparable_feature.ComparableFeature):
    '''
    TODO:
        remove the workaround to accept strings
    '''

    def __init__(self, binary_value):
        value_type = type(binary_value)
        if (value_type != int) or (value_type != bool):
            binary_value = strtobool(str(binary_value))
        self.value = bool(binary_value)

    def _similar(self, binary_feature):
        return 1. if binary_feature.value == self.value else 0.
