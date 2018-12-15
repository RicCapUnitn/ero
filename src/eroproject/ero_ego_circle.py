class EgoCircle:
    '''Defines an ego circle for a given node

    Note: the ego node is not included in the circle nodes'''

    def __init__(self, circle_name, circle_nodes):
        self.name = circle_name
        self.nodes = frozenset(circle_nodes)

    def __iter__(self):
        return self.nodes.__iter__()

    def __contains__(self, item):
        return item in self.nodes
