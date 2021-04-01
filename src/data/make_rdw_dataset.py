"""Obtain RDW data"""

import argparse
import logging
from pathlib import Path

import pandas as pd

def main(input_filepath_1, input_filepath_2, output_filepath):
  """ Runs data processing scripts to obtain RDW data.
  """
  logger = logging.getLogger(__file__)
  logger.info(f'making data set from {globals()}')

  options = dict(error_bad_lines=False, warn_bad_lines=False, 
                 parse_dates=[
    'RDW_REG_DAT_AANSPR_DAT', 'RDW_EIND_DAT_NAT_P_DAT', 'RDW_EIND_DAT_NAT_P']
                )

  rdw1 = pd.read_csv(input_filepath_1, ';',  **options)
  rdw2 = pd.read_csv(
    input_filepath_2, low_memory = False, skiprows = [130220, 131159], 
    dtype = {
      'RDW_MASSA_LEEG_VRTG_NUM': int, 
      'RDW_MAX_MASSA_VRTG_NUM': int, 
      'LAADVERMOGEN': int, 'RDW_INRICHT_CODE': int
      },
    **options
  )
  rdw2 = rdw2.drop(columns=['F' + str(integer) for integer in range(29,43)])
  rdw = pd.concat([rdw1, rdw2], ignore_index=True)
  rdw = rdw.drop_duplicates('RDW_KENTEKEN')
  rdw = rdw.set_index('RDW_KENTEKEN')
  rdw = rdw.assign(
    RDW_KVK_NR_RP = lambda x: x['RDW_KVK_NR_RP'].str[:-1].astype(float)
  )
  rdw.index = rdw.index.values + '-NL'
  rdw.to_pickle(output_filepath)


if __name__ == '__main__':
  log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  logging.basicConfig(level=logging.INFO, format=log_fmt)

  p = argparse.ArgumentParser(
  description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  p.add_argument('input_filepath_1', help='Name of first rdw file.')
  p.add_argument('input_filepath_2', help='Name of second rdw file.')
  p.add_argument('output_filepath', help='Location where result will be stored')
  args = p.parse_args()

  main(args.input_filepath_1, args.input_filepath_2, args.output_filepath)