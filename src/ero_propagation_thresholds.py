class BasePropagationThreshold():
    '''Utility class to encapsulate propagation threshold computation

    Note: all thresholds should implement this abstract class'''

    def reset(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def get_threshold(self):
        raise NotImplementedError


class StaticPropagationThreshold(BasePropagationThreshold):
    '''Threshold with static update'''

    def __init__(self):
        self.default_threshold = 0.2
        self.threshold = self.default_threshold

    def reset(self):
        self.threshold = self.default_threshold

    def update(self):
        self.threshold += 0.2

    def get_threshold(self):
        return self.threshold


class FeaturesCountBasedPropagationThreshold(BasePropagationThreshold):
    '''Threshold with dynamic updated based on the number of features'''

    def __init__(self, number_of_features, default_threshold=0.1, update_rate=0.2):
        self.number_of_features = number_of_features
        self.default_threshold = default_threshold * number_of_features
        self.threshold = self.default_threshold
        self.update_rate = update_rate

    def reset(self):
        self.threshold = self.default_threshold

    def update(self):
        self.threshold += self.update_rate

    def get_threshold(self):
        return self.threshold
