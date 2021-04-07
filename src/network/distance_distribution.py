"""
Report average distance of all pairs of nodes in graph.
"""

import argparse
import pickle
import subprocess
import tempfile

import networkx as nx
import numpy as np

def average_distance(distance_distribution: np.ndarray) -> float:
  """Return the average distance of the distance distribution."""
  return np.average(distance_distribution[:,0], weights=distance_distribution[:,1])

def diameter(distance_distribution: np.ndarray) -> int:
  """Return the diameter of the provided distance distribution."""
  return distance_distribution[:,0][-1]

def get_distance_distribution(graph: nx.Graph):
  """Determine the distance distribution of the given graph."""

  with tempfile.NamedTemporaryFile() as tmp:
    nx.write_edgelist(
      nx.convert_node_labels_to_integers(graph), 
      tmp.name, 
      delimiter='\t', 
      data=False
    )
    cp = subprocess.run(
      ['./src/teexgraph/teexgraph'], 
      input=f'load_undirected {tmp.name}\ndist_distri', 
      encoding='ascii', 
      stdout=subprocess.PIPE
    )

  return np.array(cp.stdout.split()).reshape(-1, 2).astype(int)

if __name__ == '__main__':
  p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  p.add_argument(
    'input_filepath',
    help='Name of file containing pickle of giant component of nx.Graph')
  p.add_argument('output_filepath', help='Location where result will be stored')
  args = p.parse_args()

  with open(args.input_filepath, 'rb') as file:
    gc = pickle.load(file)
  distance_distribution = get_distance_distribution(gc)
  np.savetxt(args.output_filepath, distance_distribution, fmt='%d')