from datetime import date
import logging
from pathlib import Path

import click
import pandas as pd

def merge(csv_file, zip_file, out):
  """Merge the zip and csv data."""  
  zip_data = pd.read_pickle(zip_file)
  csv_data = pd.read_pickle(csv_file)

  csv_data_ = csv_data.loc[:, list(zip_data.columns) + ['velocity', 'lane']]
  zip_data_ = zip_data[zip_data['datetime'].dt.year <= 2017].copy()

  df = pd.concat([csv_data_, zip_data_], ignore_index=True)
  df.sort_values('datetime', inplace=True)
  df.dropna(subset=['entity'], inplace=True)
  df.drop_duplicates(['entity', 'datetime'], ignore_index=True, inplace=True)
  df.to_pickle(out)

@click.command()
@click.option('--csv_file', type=click.Path(exists=True))
@click.option('--zip_file', type=click.Path(exists=True))
@click.option('--out', type=click.Path())
def main(csv_file, zip_file, out):
    """ Runs data processing scripts to turn imported data from (../1-import) 
        into merged data (saved in ../2-merge).
    """
    logger = logging.getLogger(__name__)
    logger.info(f'merge {csv_file=} and {zip_file=} to {out=}')

    merge(csv_file, zip_file, out)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    main()