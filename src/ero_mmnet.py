import glob
import re

import snap
from ero_ego_circle import EgoCircle
from ero_exceptions import ImportException


class EroMMNet:
    '''The container or the multimodal network'''

    def __init__(self):
        self.mmnet = self.generate_multimodal_network()
        self.ego_nodes = []
        self.circles = {}

        # Still to be imported
        self.people = {}
        self.events = []

        # TODO Temporary workaround to broken GetEdgeI
        # Store edgeId for crossnet PersonToPerson: (srcID,DstId)
        self.edges = {}
        # Store edgeId for crossnet EventToPerson: (srcID,DstId)
        self.event_to_person_edges = {}

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
            pattern = folder_path + '(.+).edges'
            ego_node_id = int(re.search(pattern, ego_edges_file_path).group(1))
            self.import_ego_network(ego_node_id, folder_path)

    def import_ego_network(self, ego_node_id, folder_path):
        '''Import an ego network

        ego_node_id(int)    : the # of the file #.edges
        folder_path(str)  : the directory where the file .edges is
        '''
        self.ego_nodes.append(ego_node_id)

        ego_data_path = folder_path + str(ego_node_id)
        ego_network_edges_path = ego_data_path + '.edges'
        ego_network_circles_path = ego_data_path + '.circles'

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
                # AddNode raises RuntimeError when node already present: # skip
                pass

        # Add the ego_network edges to the crossnet
        crossnet_person_to_person = self.mmnet.GetCrossNetByName(
            "PersonToPerson")
        for edge in ego_network_edges.Edges():
            edge_id = crossnet_person_to_person.AddEdge(
                edge.GetSrcNId(), edge.GetDstNId())  # TODO workaround
            self.edges[edge_id] = (
                edge.GetSrcNId(), edge.GetDstNId())  # TODO workaround

        self.import_circles(ego_node_id, ego_network_circles_path)

    def import_circles(self, ego_node_id, ego_network_circles_path):
        '''Import the ego circle for the given node'''

        with open(ego_network_circles_path) as circles_file:
            content = circles_file.readlines()
            circles = {}
            for line in content:
                stripped_line = line.strip()
                tokens = stripped_line.split()
                circle_name = tokens[0]
                circle_nodes = tokens[1:]
                circles[circle_name] = EgoCircle(circle_name, circle_nodes)

            self.circles[ego_node_id] = circles

    def propagate(self, iterations):
        '''Run the propagation algorithm'''
        for _ in range(iterations):
            for event in self.events:
                self._propagate_event_to_people(event)
        self.events.sort()

    def _propagate_event_to_people(self, event):
        '''Propagate the event information through the network'''

        propagation_threshold = 0.2
        this_iteration_reached_people = frozenset(
            self._get_event_direct_reachable_people(event.id))
        next_iteration_reachable_people = frozenset()
        already_reached_people = this_iteration_reached_people.copy()

        while len(this_iteration_reached_people) > 0:

            for person_id in this_iteration_reached_people:
                person = self.people[person_id]
                selected = person.evaluate_and_select(event)

                if selected:
                    event.relevance += 1
                    if person.best_fitness > propagation_threshold:
                        person_reachable_people = frozenset(self._get_person_direct_reachable_people(
                            person_id))
                        next_iteration_reachable_people |= person_reachable_people

            this_iteration_reached_people = next_iteration_reachable_people - already_reached_people
            already_reached_people |= this_iteration_reached_people
            next_iteration_reachable_people = frozenset()
            propagation_threshold += 0.2

    def _get_event_direct_reachable_people(self, event_id):
        '''Get the people directly connected to an event
        Params:
            event_id: the id of the event stored in the network
        Returns:
            a list of ids of people in the network
        '''
        out_edges = snap.TIntV()
        event_mode = self.mmnet.GetModeNetByName("Event")
        event_mode.GetNeighborsByCrossNet(event_id, "EventToPerson", out_edges)
        reachable_people = []
        for edge in out_edges:
            dst_id = self.event_to_person_edges[edge][1]
            reachable_people.append(dst_id)

        return reachable_people

    def _get_person_direct_reachable_people(self, person_id):
        '''Get the people directly connected to a person
        Params:
            person_id: the id of the person stored in the network
        Returns:
            a list of ids of people in the network
        '''
        out_edges = snap.TIntV()
        person_mode = self.mmnet.GetModeNetByName("Person")
        person_mode.GetNeighborsByCrossNet(
            person_id, "PersonToPerson", out_edges)
        reachable_people = []
        for edge in out_edges:
            src_id = self.edges[edge][0]
            dst_id = self.edges[edge][1]
            reachable_people.append(src_id if src_id != person_id else dst_id)

        return reachable_people
