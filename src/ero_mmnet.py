import glob
import re

import snap
from ero_ego_circle import EgoCircle
from ero_exceptions import ImportException

import numpy
from parsers import *
import json

class EroMMNet:
    '''The container or the multimodal network'''

    ''' The edge count from the events to the persons is normal distributed'''
    EVENT_PERSON_EDGES_MU = 5
    EVENT_PERSON_EDGE_SIGMA = 2

    def __init__(self):
        self.mmnet = self.generate_multimodal_network()
        self.ego_nodes = []
        self.circles = {}
        self.events = {}    # Dictionary of the evnets, key is the event id
        self.persons = []   # Array of all person ids in the network, may be converted to dictionary with person object as data

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
                self.persons.append(node.GetId())
            except RuntimeError:
                # AddNode raises RuntimeError when node already present: # skip
                pass

        # Add the ego_network edges to the crossnet
        crossnet_person_to_person = self.mmnet.GetCrossNetByName(
            "PersonToPerson")
        for edge in ego_network_edges.Edges():
            crossnet_person_to_person.AddEdge(
                edge.GetSrcNId(), edge.GetDstNId())

        # Add the ego node, which is not present in the imported
        # ego_network_edges. The ego node is linked to all the other nodes
        try:
            person_mode.AddNode(ego_node_id)
            self.persons.append(ego_node_id)
        except RuntimeError:
            pass  # AddNode raises RuntimeError when node already present: skip
        for node in ego_network_edges.Nodes():
            crossnet_person_to_person.AddEdge(
                node.GetId(), ego_node_id)

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

    def import_events(self, events_filename):
        parser = event_parser.EventParser()
        events_json = json.load(open(events_filename))['data']
        events_mode = self.mmnet.GetModeNetByName("Event")
        for event in events_json:
            parsed_event = parser.parse_event(event)
            self.events[parsed_event.event_id] = event
            events_mode.AddNode(parsed_event.event_id)
            self.connect_event_in_network(parsed_event)

    def connect_event_in_network(self, event):
        neighbors = self.generate_random_neighbors()
        crossnet_person_to_event = self.mmnet.GetCrossNetByName(
            "EventToPerson")
        for neighbor in neighbors:
            crossnet_person_to_event.AddEdge(event.event_id, neighbor)

    def generate_random_neighbors(self):
        person_max_index = len(self.persons) - 1
        edge_count = int(round(numpy.random.normal(self.EVENT_PERSON_EDGES_MU, self.EVENT_PERSON_EDGE_SIGMA, 1)))
        neighbors = []
        while len(neighbors) < edge_count:
            random_neighbor_index = numpy.random.randint(0, person_max_index)
            if self.persons[random_neighbor_index] not in neighbors:
                neighbors.append(self.persons[random_neighbor_index])
        return neighbors

    def get_event(self, event_id):
        return self.events[event_id]

