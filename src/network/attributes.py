"""
Calculate different type of assortativities.
"""
import argparse
import logging
import pickle

import networkx as nx
import pandas as pd

def set_v_median_attribute(d: pd.DataFrame, graph: nx.Graph):
  v_global_median = d['velocity'].median().round().astype('int')
  v_median = d.groupby(['entity'])['velocity'].median()
  v_median.dropna(inplace=True)
  v_median = v_median.round()
  v_median = v_median.astype(int)
  v_median = {
    n: v_median.get(n, default=v_global_median) for n in graph.nodes()}
  nx.set_node_attributes(graph, v_median, 'v_median') 

  return graph

def full(network_filepath, data_filepath, output_filepath):
  with open(network_filepath, 'rb') as file:
    g = pickle.load(file)
  with open(data_filepath, 'rb') as file:
    d = pickle.load(file)
  
  country = {node: dict(country=node.split('-')[1]) for node in g.nodes()}
  nx.set_node_attributes(g, country)

  g = set_v_median_attribute(d, g)

  nl = d.groupby('entity')['location'].nunique().to_dict()
  nx.set_node_attributes(g, nl, 'nl')

  l = d.groupby('entity')['location'].agg(lambda x:x.value_counts().index[0])
  nx.set_node_attributes(g, l.to_dict(), 'l_max')

  with open(output_filepath, 'wb') as file:
    pickle.dump(g, file)

def dutch(network_filepath, data_filepath, dutch_filepath, output_filepath):
  with open(network_filepath, 'rb') as file:
    g = pickle.load(file)
  with open(data_filepath, 'rb') as file:
    d = pickle.load(file)
  with open(dutch_filepath, 'rb') as file:
    dutch = pickle.load(file)

  g = set_v_median_attribute(d, g) 

  nl = d.groupby('entity')['location'].nunique().to_dict()
  nx.set_node_attributes(g, nl, 'nl')

  l = d.groupby('entity')['location'].agg(lambda x:x.value_counts().index[0])
  nx.set_node_attributes(g, l.to_dict(), 'l_max')

  attributes = {
    'city': 'RDW_WOONPL_NAAM',
    'm_empty': 'RDW_MASSA_LEEG_VRTG_NUM',
    'm_max': 'RDW_MAX_MASSA_VRTG_NUM',
    'capacity': 'LAADVERMOGEN',
    'company': 'RDW_NAAM'
  }
  for name, column in attributes:
    nx.set_node_attributes(g, dutch[column].dropna().to_dict(), name=name)
  
  nx.set_node_attributes(
    g, dutch['RDW_REG_DAT_AANSPR_DAT'].dt.year.dropna().astype('int').to_dict(),
    name='regdate'
  )

  for i in range(4):
    zip_data = (
      (dutch['RDW_POSTC_N'].dropna() / 10**(3-i)).astype('int').to_dict())
    nx.set_node_attributes(g, zip_data, name=f'zip{i+1}')

if __name__ == '__main__':
  p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  p.add_argument('network_filepath',
                 help='Name of file containing pickle of nx.Graph')
  p.add_argument('data_filepath',
                 help='Name of file containing pickle of the data')
  p.add_argument('rdw_filepath', help='Location of rdw datafile.')
  p.add_argument('--type', choices=['full', 'dutch'])
  p.add_argument('output_filepath', help='Location where result will be stored')
  args = p.parse_args()

  logging.debug(f'Arguments: {globals()}')

  print(args)

  if args.type == 'full':
    full(args.network_filepath, args.data_filepath, args.output_filepath)
  else:
    dutch(
      args.network_filepath, args.data_filepath, args.rdw_filepath, 
      args.output_filepath)
