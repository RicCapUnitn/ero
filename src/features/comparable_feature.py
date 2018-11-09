import abc

EMPTY_FEATURE_TYPE = None
BINARY_FEATURE_TYPE = 'binary'
DEFAULT_SIMILARITY_MISSING_FEATURES = 0


class ComparableFeature(object):
    '''All features should implement this abstract class'''

    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        raise NotImplementedError('User should define inherited subclass')

    def similar(self, other):
        '''Checks for features types match; then computes similarity'''
        if not isinstance(self, type(other)):
            if self._is_empty_feature() or other._is_empty_feature():
                return DEFAULT_SIMILARITY_MISSING_FEATURES
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
