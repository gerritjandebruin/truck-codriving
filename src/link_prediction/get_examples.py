"""Get examples used in link prediction."""

import argparse, json, logging, typing

import networkx as nx
import numpy as np
import pandas as pd
from tqdm.auto import tqdm

def depth_first_search(graph: nx.Graph, nodes: list, depthlimit: int) -> dict:
  """
  Apply a depth first search in graph, starting from all nodes. 
  Depth_limit is the maximum depth the algorithm will do the depth first 
  search on.

  Returns a dict keyed on node containing a set of all neighbours.
  """
  logging.info("Started depth first search in graph.")
  nbs = dict()
  for node in tqdm(nodes):
    nbs[node] = set()
    for u, v in nx.dfs_edges(graph, source=node, depth_limit=depthlimit):
      nbs[node].add(u)
      nbs[node].add(v)
    nbs[node].discard(node)
  logging.info("Ended depth first search in graph.")
  return nbs

def get_examples(
  graph_tau: nx.Graph, 
  depthlimit: typing.Optional[int], 
  lifetime: typing.Optional[pd.Timedelta], 
  verbose: bool = False
    ) -> list[tuple[int, int]]:
  """
  Get examples used in link prediction.

  Required arguments:
  - graph_tau: All unconnected pairs of nodes of this graph will be used.
  - depthlimit: Use only node pairs with at most this distance.
  - verbose
  """ 
  if lifetime:
    nodes = [
      node 
      for node, time in graph_tau.nodes(data='time') #type: ignore
      if time > graph_tau.graph['finalDate'] - lifetime
    ]
  else:
    nodes = list(graph_tau.nodes)

  if depthlimit:
    nbs = depth_first_search(graph_tau, nodes, depthlimit)
    return [
      (u, v) 
      for u in tqdm(nodes, desc="Generating nodepairs", disable=not verbose) 
      for v in nodes 
      if u<v and (v in nbs[u]) and ((u, v) not in graph_tau.edges)
    ]
  else:
    return [
      (u,v) 
      for u in tqdm(nodes, desc="Generating node pairs", disable=not verbose) 
      for v in nodes
      if u<v and (u,v) not in graph_tau.edges
    ]
  
if __name__ == '__main__':
  p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  p.add_argument('input_filepath', help='Filename of graph_tau')
  p.add_argument('configuration_filepath', help='Filename of configuration')
  p.add_argument(
    'output_filepath', 
    help='Location where result will be stored. Will be stored using numpy.')
  args = p.parse_args()

  logging.basicConfig(level=logging.INFO, format='%(asctime)')

  with open(args.configuration_filepath) as file:
    configuration = json.load(file)
    logging.info(f'{configuration=}')

  if configuration['lifetime_months']:
    lifetime=pd.Timedelta(days=30*configuration['lifetime_months'])
  else:
    lifetime=None
  
  examples = get_examples(
    graph_tau=pd.read_pickle(args.input_filepath),
    depthlimit=configuration['depthlimit'],
    lifetime=lifetime,
    verbose=True,
  )
  
  logging.info('Save to file.')
  np.save(args.output_filepath, examples)
  