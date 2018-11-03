import abc


class ComparableFeature(object):
    __metaclass__ = abc.ABCMeta

    def similar(self, other):
        if type(self) is not type(other):
            raise TypeError('Features of different type cannot be compared')
        return self._similar(other)

    def _similar(self, other):
        raise NotImplementedError(
            'Users must define _similar to use this base class')


def DEFAULT_NORMALIZED_COMPARISON(value1, value2):
    return abs(value1 - value2)
