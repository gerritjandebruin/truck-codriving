import networkx as nx
import numpy as np

def degree_histogram(graph: nx.Graph, num=10, weight=None):
  """
  Return the x, y, y_fit for the degree distribution of the network. The points
  are taken equi-distant in log-space.
  """
  degree_list = [d for _, d in graph.degree(weight=weight)]
  start = np.log10(2)
  stop  = np.log10(max(degree_list)+1)
  bins = np.logspace(start=start, stop=stop, num=num)
  counts, bins = np.histogram(degree_list, bins = np.round(bins))
  x = bins[:-1] + np.diff(bins)/2
  y = counts
  p0, p1 = np.polyfit(np.log10(x), np.log10(y), 1)
  y_fit = 10**(p0*np.log10(x) + p1)
  return x, y, y_fit