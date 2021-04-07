import subprocess
import tempfile

import networkx as nx
import pandas as pd

def get_diameter(graph: nx.Graph) -> int:
  """Determine the diameter of the given graph."""

  with tempfile.NamedTemporaryFile() as tmp:
    nx.write_edgelist(
      nx.convert_node_labels_to_integers(graph), 
      tmp.name, 
      delimiter='\t', 
      data=False
    )
    cp = subprocess.run(
      ['./teexgraph/teexgraph'], 
      input=f'load_undirected {tmp.name}\ndiameter', 
      encoding='ascii', 
      stdout=subprocess.PIPE
    )

  return int(cp.stdout.split()[0])

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
      ['./teexgraph/teexgraph'], 
      input=f'load_undirected {tmp.name}\ndist_distri', 
      encoding='ascii', 
      stdout=subprocess.PIPE
    )

  return cp.stdout