import snap

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

    def import_ego_network(self, ego_node_id, data_dir_path='./test/facebook/'):
        '''Import an ego network

        ego_node_id(int)    : the # of the file #.edges
        data_dir_path(str)  : the directory where the file .edges is
        '''

        ego_network_edges_path = data_dir_path + str(ego_node_id) + '.edges'
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
            person_mode.AddNode(node.GetId())

        # Add the ego_network edges to the crossnet
        crossnet_person_to_person = self.mmnet.GetCrossNetByName(
            "PersonToPerson")
        for edge in ego_network_edges.Edges():
            crossnet_person_to_person.AddEdge(
                edge.GetSrcNId(), edge.GetDstNId())

        # Add the ego node, which is not present in the imported ego_network_edges
        # The ego node is linked to all the other nodes
        person_mode.AddNode(ego_node_id)
        for node in ego_network_edges.Nodes():
            crossnet_person_to_person.AddEdge(
                node.GetId(), ego_node_id)
