"""Obtain features for link prediction."""


import argparse, logging, pickle

import networkx as nx
import numpy as np
import pandas as pd
from tqdm.auto import tqdm


def get_node_features(graph: nx.Graph, data: pd.DataFrame, verbose: bool = False 
    ) -> dict:
  """Get the node features for the link prediction problem.

  Arguments:
  - graph: graph used to create features
  - data:  pd.DataFrame containing the columns `location`, `datetime`, 
           `entityId`.

  Returns:
  - dict of dict: First key is node feature and second key is license plate. 
  """
  logging.info("Started node feature construction.")
  final_date = max([attr['time'] for n, attr in graph.nodes(data=True)]) #type: ignore
  trucks = [node for node in graph]
  d = data[(data['datetime'] <= final_date) & data['entity'].isin(trucks)]
  d = d.copy()
  # d_7 and d_30 are used for the spatiotemporal features
  d_7  = d[d['datetime'] >= final_date-pd.Timedelta(7, 'D')].copy()
  d_30 = d[d['datetime'] >= final_date-pd.Timedelta(30, 'D')].copy()

  def get_driving_hours(x): return (x.dt.hour - 12).abs().mean()
  def get_weekend(x): return (x.dt.weekday >= 5).mean()
  # See paper for definitions of these node features.
  node_features = {
    "country": {node: node.split('-')[1] for node in graph},
    "ax": d.groupby("entity")["axes"].median().fillna(0).to_dict(), #type: ignore
    "length": d.groupby("entity")["length"].median().fillna(0).to_dict(), #type: ignore
    "m": d.groupby("entity")["mass"].median().fillna(0).to_dict(), #type: ignore
    "night": d.groupby("entity")["datetime"].agg(get_driving_hours).to_dict(), #type: ignore
    "weekend": d.groupby("entity")["datetime"].agg(get_weekend).to_dict(), #type: ignore
    "nb": {n: set(graph[n]) for n in graph},
    "vol": {n: sum([w for _, _, w in graph.edges(nbunch=n, data="weight")]) #type: ignore
            for n in graph},
    "shortest_path": {n: dict(nx.single_source_shortest_path_length(graph, n)) 
                     for n in tqdm(graph, "shortest_path per node")},
    # Contains for every location the nuber of registrations in last
    # x days.
    "f_7":  d_7.groupby( ["entity", "location"]).size().to_dict(),
    "f_30": d_30.groupby(["entity", "location"]).size().to_dict(),
    # 365 equals all measurements.
    "f_365": d.groupby(  ["entity", "location"]).size().to_dict() 
  }

  logging.info("Ended node feature construction.")
  return node_features

def get_features(
  graph_tau: nx.Graph, data: pd.DataFrame, examples: list[tuple[int, int]], 
  verbose: bool = False
  ) -> pd.DataFrame:
  """Returns the features for the link prediction problem.

  Args:
  - graph: Used to determine the features from.
  - data: Used to construct the features from.
  - index: List of pairs of nodes for which the features are constructed.
  """
  logging.info("Start feature construction.")

  node_features = get_node_features(graph=graph_tau, data=data)

  logging.info("Create pd.DataFrame with index.")
  x = pd.DataFrame(index=examples)

  x["truck_ax_sum"] = [
    node_features["ax"][u] + node_features["ax"][v] 
    for u, v in tqdm(examples, desc="truck_ax_sum", disable=not verbose)]
  x["truck_ax_diff"] = [
    abs(node_features["ax"][u] - node_features["ax"][v]) 
    for u, v in tqdm(examples, desc="truck_ax_diff", disable=not verbose)]          
  x["truck_len_sum"] = [
    node_features["length"][u] + node_features["length"][v] 
    for u, v in tqdm(examples, desc="truck_len_sum", disable=not verbose)]
  x["truck_len_diff"] = [
    abs(node_features["length"][u] - node_features["length"][v]) 
    for u, v in tqdm(examples, desc="truck_len_diff", disable=not verbose)]
  x["truck_mass_sum"] = [
    node_features["m"][u] + node_features["m"][v] 
    for u, v in tqdm(examples, desc="truck_mass_sum", disable=not verbose)]
  x["truck_mass_diff"] = [
    abs(node_features["m"][u] - node_features["m"][v]) 
    for u, v in tqdm(examples, desc="truck_mass_diff", disable=not verbose)]
  x["night_sum"] = [
    node_features["night"][u] + node_features["night"][v] 
    for u, v in tqdm(examples, desc="night_sum", disable=not verbose)]
  x["night_diff"] = [
    abs(node_features["night"][u] - node_features["night"][v]) 
    for u, v in tqdm(examples, desc="night_diff", disable=not verbose)]
  x["weekend_sum"] = [
    node_features["weekend"][u] + node_features["weekend"][v]
    for u, v in tqdm(examples, desc="weekend_sum", disable=not verbose)]
  x["weekend_diff"] = [
    abs(node_features["weekend"][u] - node_features["weekend"][v]) 
    for u, v in tqdm(examples, desc="weekend_diff", disable=not verbose)]
  x["degree_sum"] = [
    len(node_features["nb"][u]) + len(node_features["nb"][v]) 
    for u, v in tqdm(examples, desc="degree_sum", disable=not verbose)]
  x["degree_diff"] = [
    abs(len(node_features["nb"][u]) - len(node_features["nb"][v]))
    for u, v in tqdm(examples, desc="degree_diff", disable=not verbose)]
  x["volume_sum"] = [
    node_features["vol"][u] + node_features["vol"][v] 
    for u, v in tqdm(examples, desc="volume_sum", disable=not verbose)]
  x["volume_diff"] = [
    abs(node_features["vol"][u] - node_features["vol"][v])
    for u, v in tqdm(examples, desc="volume_diff", disable=not verbose)]       
  x["country_same"] = [
    node_features["country"][u] == node_features["country"][v]
    for u, v in tqdm(examples, desc="country_same", disable=not verbose)]
  x["nb_total"] = [
    len(node_features["nb"][u] | node_features["nb"][v])
    for u, v in tqdm(examples, desc="nb_total", disable=not verbose)]
  x["nb_common"] = [
    len(node_features["nb"][u] & node_features["nb"][v])
    for u, v in tqdm(examples, desc="nb_common", disable=not verbose)]
  x["shortest_path"] = [
    node_features["shortest_path"][u].get(v, 100)
    for u, v in tqdm(examples, desc="shortest_path", disable=not verbose)]

  locations = {loc for _, loc in node_features["f_365"].keys()}
  for location in tqdm(locations, desc="spatiotemporal features", 
                       disable=not verbose):
    x[f'f_7_{location}'] = [
      node_features["f_7"].get((u, location), 0) 
      + node_features["f_7"].get((v, location), 0)
      for u, v in examples
    ]
    x[f'f_30_{location}'] = [
      node_features["f_30"].get((u, location), 0) 
      + node_features["f_30"].get((v, location), 0)
      for u, v in examples
    ]
    x[f'f_365_{location}'] = [
      node_features["f_365"].get((u, location), 0) + 
      node_features["f_365"].get((v, location), 0)
                              for u, v in examples]

  return x.loc[:, x.any()] #type: ignore Remove columns with only zeros.

if __name__ == '__main__':
  p = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  p.add_argument('input_graph_tau', help='Name of file containing graph.')
  p.add_argument('input_data', help='File location of data.')
  p.add_argument('input_examples', help='File location containing examples.')
  p.add_argument(
    'output_filepath', help='Location where result will be stored.')
  args = p.parse_args()

  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
  
  logging.info('Read graph tau')
  with open(args.input_graph_tau, 'rb') as file:
    graph_tau = pickle.load(file)
  
  features = get_features(
    graph_tau=graph_tau,
    data=pd.read_pickle(args.input_data),
    examples=np.load(args.input_examples),
    verbose=True
  )

  logging.info('Save to file')
  features.to_pickle(args.output_filepath)