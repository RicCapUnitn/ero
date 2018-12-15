import ero_mmnet
from ero_exceptions import ImportException


class Ero:
    '''The class that represents the system.'''

    def __init__(self, do_crossover=False):
        self.mmnet = ero_mmnet.EroMMNet(do_crossover)

    def import_ego_networks_folder(self, folder_path):
        '''Import all ego networks in a folder into the system

        Args:
            folder_path: the path of the folder where the files .edges are
        '''
        self.mmnet.import_ego_networks_folder(folder_path)

    def import_ego_network(self, ego_node_id, folder_path):
        '''Import the people network in the system

        Args:
            ego_node_id: the ego_node_id that identifies the network
            folder_path: the path of the folder where the files .edges are
        '''
        try:
            self.mmnet.import_ego_network(ego_node_id, folder_path)
        except ImportException as exc:
            raise UserWarning("Failed to import ego network: " + str(exc))

    def import_events(self, events_filename):
        self.mmnet.import_events(events_filename)
