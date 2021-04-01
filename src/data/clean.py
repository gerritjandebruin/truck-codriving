from datetime import date
import logging
from pathlib import Path

import click
import pandas as pd

def clean(input_filepath, output_filepath, min_measured):
  """Clean the provided data."""  
  data = pd.read_pickle(input_filepath)

  # Apply several data cleaning steps.
  m_loc = data["location"].str[:3].isin(["A12", "A15", "A16"])
  m_side = data["location"].str[-1].isin(["L", "R"])
  m_time = data["datetime"].dt.year + data["datetime"].dt.month/12 <= 2018.5
  m_lp = data["location"].str.len() > 7
  m_country = ~data["country"].isin(["X_E", "D/N", "?"])

  data = data[m_loc & m_side & m_time & m_lp & m_country]

  # Use only trucks that are measured at least min_measured times.
  x = data["entity"].value_counts().sort_index()
  data = data.loc[data["entity"].isin(x.loc[x >= min_measured].index)]
  data.sort_values("datetime", inplace=True)
  data.reset_index(drop=True, inplace=True)
  data = data.astype({'entity': 'category'})

  # Some clarification regarding locations.
  data['location'] = data['location'].astype('category')
  data["location"] = (
      data["location"].cat.rename_categories({
          "A12 41.8 L": "A12 L Woerden",
          "A12 42.7 R": "A12 R Woerden",
          "A15 91.6 R": "A15 R Giessenburg",
          "A15 91.7 L": "A15 L Giessenburg",
          "A16 40.9 R": "A16 R Dordrecht",
          "A16 41.5 L": "A16 L Dordrecht"})
      .cat.remove_unused_categories()
  )
  
  data.to_pickle(output_filepath)

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
@click.option('--min_measured', type=int, default=1)
def main(input_filepath, output_filepath, min_measured):
    """ Runs data processing scripts to turn merged data from (../2-merge) into
        cleaned data ready to be analyzed (saved in ../3-process).
    """
    logger = logging.getLogger(__file__)
    logger.info(f'clean {input_filepath=} to {output_filepath=}')

    clean(input_filepath, output_filepath)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    main()