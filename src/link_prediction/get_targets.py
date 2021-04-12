"""Get targets."""

import argparse, logging, pickle

import networkx as nx
import numpy as np
from tqdm.auto import tqdm

def get_targets(graph: nx.Graph, examples: list, verbose: bool = False) -> list:
  """Get the labels for the link prediction."""
  edges = {(u,v) if u < v else (v,u) for u, v in graph.edges}
  return [
    (u,v) in edges 
    for (u, v) in tqdm(examples, desc="Get targets", disable=not verbose)
  ]

if __name__ == '__main__':
  p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  p.add_argument('input_graph', help='Name of file containing graph.')
  p.add_argument(
    'input_examples', help='Location of file containing the examples.')
  p.add_argument(
    'output_filepath', 
    help='Location where result will be stored. Will be stored using numpy.')
  args = p.parse_args()
  
  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

  logging.info('Load graph.')
  with open(args.input_graph, 'rb') as file:
    graph = pickle.load(file)
  
  logging.info('Get targets.')
  targets = get_targets(
    graph, examples=np.load(args.input_examples), verbose=True)

  logging.info('Save targets to file.')
  np.save(args.output_filepath, targets)