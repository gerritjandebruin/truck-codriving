"""
Get giant component of networkx Graph.
"""

import argparse

import networkx as nx

def giant_component(graph: nx.Graph) -> nx.Graph:
  """Returns the giant component of provided graph."""
  return max(
    (graph.subgraph(c) for c in nx.connected_components(graph)), key=len)

if __name__ == '__main__':
  p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  p.add_argument('input_filepath',
                 help='Name of file containing pickle of nx.Graph', 
                 type=argparse.FileType('r'))
  p.add_argument('output_filepath', help='Location where result will be stored',
                 type=argparse.FileType('w'))
  args = p.parse_args()

  nx.write_gpickle(
    giant_component(nx.read_gpickle(args.input_filepath)),
    args.output_filepath
    )