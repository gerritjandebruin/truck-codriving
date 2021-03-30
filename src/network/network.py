import networkx as nx
from .cooccurrence import Cooccurrence

def add_edge(graph: nx.Graph, u: str, v: str) -> None:
  """Add edge to graph. If already exists, add one weight."""
  if not graph.has_edge(u,v): graph.add_edge(u, v, weight=1)
  else: graph.add_edge(u, v, weight=graph[u][v]['weight'] + 1)

def create_graph(cooccurrences: list[Cooccurrence]) -> nx.Graph:
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

def giant_component(graph: nx.Graph) -> nx.Graph:
  """Returns the giant component of provided graph."""
  return max(
    (graph.subgraph(c) for c in nx.connected_components(graph)), key=len)