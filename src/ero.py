import ero_mmnet
import warnings

from ero_exceptions import ImportException


class Ero():
    '''The class that represents the system.'''

    def __init__(self):
        self.mmnet = ero_mmnet.EroMMNet()

    def import_ego_network(self, ego_node_id):
        '''Import the people network in the system

        Args:
            ego_node_id: the ego_node_id that identifies the network
        '''
        try:
            self.mmnet.import_ego_network(ego_node_id)
        except ImportException as exc:
            raise Warning("Failed to import ego network: " + str(exc))
