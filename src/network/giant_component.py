"""
Get giant component of networkx Graph.
"""

import argparse
import pickle

import networkx as nx

def giant_component(graph: nx.Graph) -> nx.Graph:
  """Returns the giant component of provided graph."""
  return max(
    (graph.subgraph(c) for c in nx.connected_components(graph)), key=len)

if __name__ == '__main__':
  p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  p.add_argument('input_filepath',
                 help='Name of file containing pickle of nx.Graph')
  p.add_argument('output_filepath', help='Location where result will be stored')
  args = p.parse_args()

  with open(args.input_filepath, 'rb') as file:
    g = pickle.load(file)
  gc = giant_component(g)
  with open(args.output_filepath, 'wb') as file:
    pickle.dump(gc, file)