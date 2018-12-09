import glob
import json
import re

import numpy

import snap
from ero_ego_circle import EgoCircle
from ero_exceptions import ImportException
from parsers import *


class EroMMNet:
    '''The container or the multimodal network'''

    ''' The edge count from the events to the people is normal distributed'''
    EVENT_PERSON_EDGES_MU = 5
    EVENT_PERSON_EDGE_SIGMA = 2

    '''Maximum distance an event propagation can reach from the propagating event'''
    PROPAGATION_DISTANCE_THRESHOLD = 4

    def __init__(self, do_crossover):
        self.mmnet = self.generate_multimodal_network()
        self.ego_nodes = []
        self.circles = {}

        # TODO make the two dictionaries become classes
        self.events = {}  # event_id : Event
        self.people = {}  # person_id: Person

        # TODO Temporary workaround to broken GetEdgeI
        # Store edgeId for crossnet PersonToPerson: (srcID,DstId)
        self.person_to_person_edges = {}
        # Store edgeId for crossnet EventToPerson: (srcID,DstId)
        self.event_to_person_edges = {}

        # TODO the path here is hardcoded, should be put as parameter
        comparable_features = json.load(
            open('test/istat/comparable_features.json'))
        self.comparable_features = sorted(comparable_features['features'])

        self.do_crossover = do_crossover

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
            folder_path(str): the directory where the file .edges is
        '''
        ego_network_edges_iterator = glob.iglob(folder_path + '*.edges')
        for ego_edges_file_path in ego_network_edges_iterator:
            pattern = folder_path + '(.+).edges'
            ego_node_id = int(re.search(pattern, ego_edges_file_path).group(1))
            self.import_ego_network(ego_node_id, folder_path)

    def import_ego_network(self, ego_node_id, folder_path):
        '''Import an ego network

        ego_node_id(int): the  # of the file #.edges
        folder_path(str): the directory where the file .edges is
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
            self.person_to_person_edges[edge_id] = (
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
                circle_nodes = [int(token) for token in tokens[1:]]
                circles[circle_name] = EgoCircle(circle_name, circle_nodes)

            self.circles[ego_node_id] = circles

    def propagate(self, iterations, reset_propagation=True):
        '''Run the propagation algorithm'''
        for _ in range(iterations):

            if reset_propagation:
                self.reset_propagation()

            if self.do_crossover:
                self._do_crossover()

            for event in self.events.values():
                self._propagate_event_to_people(event)

    def reset_propagation(self):
        '''Reset all defaults after propagation'''
        for person in self.people.values():
            person.reset()
        for event in self.events.values():
            event.reset()

    def _propagate_event_to_people(self, event):
        '''Propagate the event information through the network

        Note: to avoid using a propagation threshold we added a factor of distance
        to the event in the computation of the fitness; the greater the distance
        (where distance is the number of edges between the person and the event
        node), the lower the resulting fitness (the less chance the event has to
        be chosen and further propagated).
        '''

        event_distance = 1

        this_iteration_reached_people = frozenset(
            self._get_event_direct_reachable_people(event.id))
        next_iteration_reachable_people = frozenset()
        already_reached_people = this_iteration_reached_people.copy()

        while (len(this_iteration_reached_people) > 0) and \
                (event_distance < self.PROPAGATION_DISTANCE_THRESHOLD):

            for person_id in this_iteration_reached_people:
                person = self.people[person_id]
                selected = person.mutate_evaluate_and_select(
                    event, event_distance)

                if selected:
                    event.relevance += 1
                    person_reachable_people = frozenset(self._get_person_direct_reachable_people(
                        person_id))
                    next_iteration_reachable_people |= person_reachable_people

            this_iteration_reached_people = next_iteration_reachable_people - already_reached_people
            already_reached_people |= this_iteration_reached_people
            next_iteration_reachable_people = frozenset()
            event_distance += 1

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
            src_id = self.person_to_person_edges[edge][0]
            dst_id = self.person_to_person_edges[edge][1]
            reachable_people.append(src_id if src_id != person_id else dst_id)

        return reachable_people

    def import_events(self, events_filename):
        parser = event_parser.EventParser(self.comparable_features)
        events_json = json.load(open(events_filename))['data']
        events_mode = self.mmnet.GetModeNetByName("Event")
        for event in events_json:
            parsed_event = parser.parse_event(event)
            self.events[parsed_event.id] = parsed_event
            events_mode.AddNode(parsed_event.id)
            self.connect_event_in_network(parsed_event)

    def connect_event_in_network(self, event):
        neighbors_ids = self.generate_random_neighbors()
        crossnet_person_to_event = self.mmnet.GetCrossNetByName(
            "EventToPerson")
        for neighbor_id in neighbors_ids:
            edge_id = crossnet_person_to_event.AddEdge(event.id, neighbor_id)
            self.event_to_person_edges[edge_id] = (
                event.id, neighbor_id)

    def generate_random_neighbors(self):
        edge_count = int(round(numpy.random.normal(
            self.EVENT_PERSON_EDGES_MU, self.EVENT_PERSON_EDGE_SIGMA, 1)))
        neighbors_ids = []
        for _ in range(edge_count):
            random_neighbor_id = numpy.random.randint(0, len(self.people))
            neighbors_ids.append(random_neighbor_id)
        return neighbors_ids

    def get_event(self, event_id):
        return self.events[event_id]

    def _do_crossover(self):
        '''Croossover weights of people that belong to the same circle

        For each circle we compute mean of each feature and we decrease the feature
        variance (moving each value towards the mean given a set crossover_rate)'''

        CROSSOVER_RATE = 0.1

        for ego_circles in self.circles.values():
            for ego_circle in ego_circles.values():
                circle_people = [self.people[person_id]
                                 for person_id in ego_circle]
                number_of_features = len(circle_people[0].features)
                for index in range(number_of_features):
                    circle_feature_weights = [person.features_weights[index]
                                              for person in circle_people]
                    feat_mean = numpy.mean(circle_feature_weights)
                    # Move each value towards the mean
                    self._normalize_features(
                        circle_people, index, feat_mean, CROSSOVER_RATE)

    def _normalize_features(self, people, feature_index, feature_mean, crossover_rate):
        for person in people:
            person.features_weights[feature_index] += (feature_mean -
                                                       person.features_weights[feature_index]) * crossover_rate
