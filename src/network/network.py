import logging, pickle, typing

import click
import networkx as nx
import pandas as pd

from .cooccurrence import Cooccurrence

def add_edge(graph: nx.Graph, u: str, v: str) -> None:
  """Add edge to graph. If already exists, add one weight."""
  if not graph.has_edge(u,v): graph.add_edge(u, v, weight=1)
  else: graph.add_edge(u, v, weight=graph[u][v]['weight'] + 1)

def create_graph(cooccurrences: typing.Union[list[Cooccurrence], pd.DataFrame]
    ) -> nx.Graph:
  """Create weighted graph from a sorted list of cooccurrences."""
  graph = nx.Graph(None, final_date=None)
  for cooccurrence in cooccurrences:
    u = cooccurrence.event
    v = cooccurrence.other_event
    graph.add_node(u.entity, time=u.time)
    graph.add_node(v.entity, time=v.time)
    add_edge(graph, u.entity, v.entity)
  graph.graph['finalDate'] = cooccurrences[-1].time
  return graph

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
  logger = logging.getLogger(__file__)
  logger.info(f'Load cooccurrences, args: {locals()}')
  with open(input_filepath, 'rb') as file:
    cooccurrences = pickle.load(file)

  logger.info(f'Create network')
  graph = create_graph(cooccurrences)

  logger.info(f'Dump graph')
  with open(output_filepath, 'wb') as file:
    pickle.dump(graph, file)

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()