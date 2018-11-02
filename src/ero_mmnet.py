import snap
import glob
import re

from ero_exceptions import ImportException


class EroMMNet():
    '''The container or the multimodal network'''

    def __init__(self):
        self.mmnet = self.generate_multimodal_network()

    def generate_multimodal_network(self):
        '''Generate the multimodal network

        Two modes are created: Event and Person
        Two crossnets are created:
            EventToPerson, directed links; PersonToPerson, undirected'''

        mmnet = snap.TMMNet.New()
        mmnet.AddModeNet("Event")
        mmnet.AddModeNet("Person")
        mmnet.AddCrossNet("Event", "Person", "EventToPerson", True)
        mmnet.AddCrossNet("Person", "Person", "PersonToPerson", False)

        return mmnet

    def import_ego_networks_folder(self, folder_path):
        '''Import all ego networks in a folder

        Args:
            folder_path(str)  : the directory where the file .edges is
        '''
        ego_network_edges_iterator = glob.iglob(folder_path + '*.edges')
        for ego_edges_file_path in ego_network_edges_iterator:
            pattern = folder_path + '(.+).edges'  # folder/#.edges
            ego_node_id = int(re.search(pattern, ego_edges_file_path).group(1))
            self.import_ego_network(ego_node_id, folder_path)

    def import_ego_network(self, ego_node_id, folder_path='./test/facebook/'):
        '''Import an ego network

        ego_node_id(int)    : the # of the file #.edges
        folder_path(str)  : the directory where the file .edges is
        '''

        ego_network_edges_path = folder_path + str(ego_node_id) + '.edges'
        try:
            ego_network_edges = snap.LoadEdgeList(
                snap.PUNGraph,
                ego_network_edges_path, 0, 1, ' ')
        except RuntimeError as exc:
            raise ImportException('File not found: {}'.format(
                ego_network_edges_path))

        # Add nodes to the person mode
        person_mode = self.mmnet.GetModeNetByName("Person")
        for node in ego_network_edges.Nodes():
            try:
                person_mode.AddNode(node.GetId())
            except RuntimeError:
                # AddNode raises RuntimeError when node is already present: skip
                pass

        # Add the ego_network edges to the crossnet
        crossnet_person_to_person = self.mmnet.GetCrossNetByName(
            "PersonToPerson")
        for edge in ego_network_edges.Edges():
            crossnet_person_to_person.AddEdge(
                edge.GetSrcNId(), edge.GetDstNId())

        # Add the ego node, which is not present in the imported ego_network_edges
        # The ego node is linked to all the other nodes
        try:
            person_mode.AddNode(ego_node_id)
        except RuntimeError:
            # AddNode raises RuntimeError when node is already present: skip
            pass
        for node in ego_network_edges.Nodes():
            crossnet_person_to_person.AddEdge(
                node.GetId(), ego_node_id)
