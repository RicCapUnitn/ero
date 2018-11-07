import abc

EMPTY_FEATURE_TYPE = None
BINARY_FEATURE_TYPE = 'binary'


class ComparableFeature(object):
    '''All features should implement this abstract class'''

    __metaclass__ = abc.ABCMeta
    DEFAULT_SIMILARITY_MISSING_FEATURES = 0

    def __init__(self, *args, **kwargs):
        raise NotImplementedError('User should define inherited subclass')

    def similar(self, other):
        '''Checks for features types match; then computes similarity'''
        if not isinstance(self, type(other)):
            if self._is_empty_feature() or other._is_empty_feature():
                return self.DEFAULT_SIMILARITY_MISSING_FEATURES
            else:
                raise TypeError(
                    'Features of different type cannot be compared')
        return self._similar(other)

    def _similar(self, other):
        '''Compute the similarity between this feature and another feature

        Args:
            other: the other feature of the same type
        Note:
            Implement this function to extend the class
        '''
        raise NotImplementedError(
            'Users must define _similar to use this base class')

    def _is_empty_feature(self):
        return self.value is EMPTY_FEATURE_TYPE


def DEFAULT_NORMALIZED_COMPARISON(value1, value2):
    return abs(value1 - value2)
