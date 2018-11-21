#!/usr/bin/env

import os
import sys
library_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, library_path + '/../../src')

import snap

network = '0.edges'

graph = snap.LoadEdgeList(snap.PUNGraph, network, 0, 1, ' ')

labels = True
snap.DrawGViz(graph, snap.gvlDot, network + '.png', network, labels)
