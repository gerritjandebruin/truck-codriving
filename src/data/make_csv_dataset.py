import os
import logging
from pathlib import Path

import click
import numpy as np
import pandas as pd
from tqdm.auto import tqdm

def get_csv_data(input_filepath, output_filepath):
  d = pd.concat(
    [
      pd.read_csv(f'{input_filepath}/{file}', engine='python', encoding='latin')
      for file in tqdm(os.listdir(input_filepath), desc='Reading', unit='file')
    ]
  )
  t = d['LABEL'].str.split(' ',expand=True)
  t[1] = t[1].str.strip('0')
  t[4] = t[4].str.replace(',', '.')
  d['location'] = 'A' + t[1] + ' ' + t[4] + ' ' + t[3]
  d.rename(columns=dict(SNELHEID='velocity', TOTAALGEWICHT='mass', 
                        LENGTE='length', STROOKVOLGNUMMER='lane'), 
           inplace=True)
  d['datetime'] = pd.to_datetime(d['UTCPASSAGEDATUM'].astype(str) + '0000', 
                                 format='%d%b%Y:%H:%M:%S.%f')
  t = {'-': '?', 'AUT': 'AT', 'B': 'BE', 'BEL': 'BE', 'BGR': 'BG', 'BLR': 'BY', 
       'CHE': 'CH', 'CZE': 'CZ', 'D': 'DE', 'D/N': '?', 'DEU': 'DE', 
       'DNK': 'DK', 'Du': 'DE', 'E': 'ES', 'ESP': 'ES', 'EST': 'EE', 'F': 'FR', 
       'FIN': 'FI', 'FRA': 'FR', 'Fr': 'FR', 'GBR': 'GB', 'GRC': 'GR', 
       'HUN': 'HU', 'I': 'IT', 'IRL': 'IE', 'ITA': 'IT', 'LTU': 'LT', 
       'LUX': 'LU', 'LVA': 'LV', 'N': 'NL', 'NLD': 'NL', 'P': 'PT', 'PRT': 'PT', 
       'POL': 'PO', 'ROU': 'RO', 'RUS': 'RU', 'SRB': 'RS', 'SVK': 'SE', 
       'SVN': 'SI', 'SWE': 'SE', 'UNK': 'UA', 'X_E': '?'}
  d['country'] = d['LANDCODEVOOR'].fillna('?').replace(t)
  d['entity'] = (d['KENTEKENVOOR'] + '-' + d['country']).str.upper()
  d['axes'] = d[[f'asdruk{i}' for i in np.arange(1, 9)]].notna().sum(axis=1)
  
  d.sort_values('datetime', inplace=True)
  d.to_pickle(output_filepath)

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../0-raw/csv) into
        serialized data ready to be used in Pandas (saved in ../1-import).
    """
    logger = logging.getLogger(__name__)
    logger.info(f'making data set from {input_filepath}')

    get_csv_data(input_filepath, output_filepath)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    main()