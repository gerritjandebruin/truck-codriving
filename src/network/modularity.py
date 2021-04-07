import tempfile

import igraph
import leidenalg
import networkx as nx

def get_modularity(graph: nx.Graph) -> float:
  """Get the maximum modularity using Leiden algorithm."""
  graph_without_attributes = nx.Graph()
  graph_without_attributes.add_edges_from(graph.edges())

  with tempfile.TemporaryDirectory() as tmpdirname:
    nx.write_graphml(graph_without_attributes, f'{tmpdirname}/temp.graphml')
    Gix = igraph.read(f'{tmpdirname}/temp.graphml', format='graphml')

  part = leidenalg.find_partition(Gix, leidenalg.ModularityVertexPartition)

  return part.modularity