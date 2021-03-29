import logging
import os

import click
import pandas as pd
import joblib

from event import get_events, Event
from cooccurrence import get_cooccurrences, divide_cooccurrences
from network import create_graph, giant_component

def pipeline(
    events: list[Event], output_filepath: str, *,
    Δt_max: float, min_timedelta: float):
  """Returns the systematic and random cooccurrences resp. for the parameters.
  """
  os.makedirs(output_filepath, exist_ok=True)

  logger = logging.getLogger(__name__)
  if 'systematic.pkl' in os.listdir(output_filepath):
    logger.error(
      f'{os.path.join(output_filepath, "systematic.pkl")} already exists')

  logger.info(f'Start pipeline for {Δt_max=}')
  cooccurrences = get_cooccurrences(events, 
                                    max_timedelta=pd.Timedelta(f'{Δt_max}s'))
  
  logger.info(f'Divide cooccurrences for {Δt_max=}')
  systematic, random = divide_cooccurrences(cooccurrences, 
                                            min_timedelta=min_timedelta)
  
  logger.info(f'Dump systematic, random for {Δt_max=}')
  joblib.dump(systematic, os.path.join(output_filepath, 'systematic.pkl'))
  joblib.dump(random, os.path.join(output_filepath, 'random.pkl'))
  
  logger.info(f'Create graph for {Δt_max=}')
  graph = create_graph(systematic)
  
  logger.info(f'Dump graph for {Δt_max=}')
  joblib.dump(graph, os.path.join(output_filepath, 'graph.pkl'))

  logger.info(f'Get and dump giant_component for {Δt_max=}')
  joblib.dump(giant_component(graph), 
              os.path.join(output_filepath, 'giant_component.pkl'))

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
@click.option('--dt_max_list', '-dt', type=int, multiple=True)
@click.option('--min_timedelta', default=pd.Timedelta('3h'))
def main(input_filepath, output_filepath, dt_max_list, min_timedelta):
  logger = logging.getLogger(__name__)
  logger.info(f'Start making networks, args: {locals()}')
  data = joblib.load(input_filepath)
  events = get_events(data=data)

  joblib.Parallel(n_jobs=len(dt_max_list))(
    joblib.delayed(pipeline)(
      events, 
      output_filepath=os.path.join(output_filepath, str(int(Δt_max))),
      Δt_max=Δt_max, 
      min_timedelta=min_timedelta)
    for Δt_max in dt_max_list
  )

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()