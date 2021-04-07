"""Get graph_tau, which will be used for feature construction."""

import argparse, json, logging,pickle

import networkx as nx
import pandas as pd

from ..network import create_graph, Cooccurrence, giant_component

def get_graph_tau(edgelist: pd.DataFrame, tau: float) -> nx.Graph:
  """
  Get examples used in link prediction.

  Required arguments:
  - graph: All unconnected pairs of nodes of this graph will be used.
  OR
  - data: Create graph of these edges.
  - tau: Use only the first tau fraction of edges, assumming that edgelist is
      already sorted on time. The unconnected pairs of nodes of this graph will
      be used.

  Optional arguments:
  - depthlimit: Use only node pairs with at most this distance.
  - verbose
  """  
  stop_index = int(len(edgelist) * tau)
  return create_graph(edgelist[:stop_index])
  
if __name__ == '__main__':
  p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  p.add_argument('input_filepath', help='Filename of data')
  p.add_argument('configuration_filepath', help='Filename of configuration')
  p.add_argument(
    '--tau', type=float, 
    help='Use only the first tau fraction of edges, assuming that edgelist is'
      'already sorted on time. The unconnected pairs of nodes of graph obtained'
      'from these edges will be returned.')
  p.add_argument(
    'output_filepath', 
    help='Location where result will be stored. Will be stored using pickle.')
  args = p.parse_args()

  logging.basicConfig(level=logging.INFO)
  
  with open(args.configuration_filepath) as file:
    configuration = json.load(file)
  logging.info(f'{configuration=}')
  
  graph_tau = get_graph_tau(
    edgelist=pd.read_pickle(args.input_filepath), tau=configuration['tau'])

  if configuration['giant_component']:
    graph_tau = giant_component(graph_tau)

  with open(args.output_filepath, 'wb') as file:
    pickle.dump(graph_tau, file)
  