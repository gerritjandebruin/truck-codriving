import os
import logging
from pathlib import Path
import re
import zipfile

import click
import pandas as pd
from tqdm.auto import tqdm

def get_zip_data(input_filepath, output_filepath):
    """Read in the source files provided in filepath."""  
    # Datalist is list containing a pd.DataFrame for each file.
    datalist = list()
    try: files = list(os.scandir(input_filepath))
    except: raise Exception(f"Could not read {input_filepath}.")
    
    for file in tqdm(files, desc="Reading zip files"):
        with zipfile.ZipFile(file.path) as zipbestand:
            for bestandeninzip in zipbestand.namelist():
                with zipbestand.open(bestandeninzip) as bestandinzip:
                    datalist.append(
                        pd.read_csv(bestandinzip, sep=';', 
                                    encoding='ISO-8859-1',
                                    usecols=["LPN_REQ", 
                                             "VIGNETT_INSPECTION_REQ",
                                             "LANDCODE", "LOCATIE_CODE",
                                             "TOTAAL_GESCAND_GEWICHT", 
                                             "LENGTE_COMBINATIE",
                                             "AANTAL_ASGROEPEN"],
                                    dtype={'AANTAL_ASGROEPEN': "Int8", 
                                           'LPN_REQ': "category",
                                           'LOCATIE_CODE': "category"},
                                    parse_dates=["VIGNETT_INSPECTION_REQ"]))

    # Concatinate the list of dataframes to one dataframe.
    data = pd.concat(datalist, ignore_index=True)

    # Some renaming of columns.
    data.rename(columns={"LPN_REQ": "entity",
                         "VIGNETT_INSPECTION_REQ": "datetime",
                         "LANDCODE": "country",
                         "LOCATIE_CODE": "location",
                         "TOTAAL_GESCAND_GEWICHT": "mass",
                         "LENGTE_COMBINATIE": "length",
                         "AANTAL_ASGROEPEN": "axes"}, inplace=True)

    # Rename some locations and countries.
    data = data.replace(
      {'location': {item: "A" + re.sub(r"\D", "", item[2:5])[:-1] + " " +
                    str(int(re.sub(r"\D", "", item[-4:])) / 10) + " " + 
                    item.split("HR")[1][0] 
                    for item in data["location"].unique()},
       'country': {
         'ARE': 'AE', 'AUT': 'AT', 'B': 'BE', 'BEL': 'BE', 'BGR': 'BU', 
         'BLR': 'BY', 'CHE': 'CH', 'CZE': 'CZ', 'D': 'DE', 'DEU': 'DE', 
         'DNK': 'DK', 'Du': 'DE', 'E': 'ES', 'ESP': 'ES', 'EST': 'EE', 
         'F': 'FR', 'FIN': 'FI', 'FRA': 'FR', 'Fr': 'FR', 'GBR': 'GB', 
         'GRC': 'GR', 'HRV': 'HR', 'HUN': 'HO', 'I': 'IT', 'IRL': 'IE', 
         'ITA': 'IT', 'LTU': 'LT', 'LUX': 'LU', 'LVA': 'LV', 'N': 'NL', 
         'NLD': 'NL', 'P': 'PT', 'POL': 'PO', 'PRT': 'PT', 'ROU': 'RO', 
         'RUS': 'RU', 'SRB': 'RS', 'SVK': 'SK', 'SVN': 'SI', 'SWE': 'SE', 
         'TUR': 'TR', 'UNK': 'UK'}})

    # Add country code to license plate.
    data["entity"] = data["entity"] + '-' + data["country"]   

    # Optimize some memory performance by turning some columns to categories.
    data = data.astype(dict(location="category", country="category")) 

    # Drop duplicate items.
    data.drop_duplicates(subset=["entity", "datetime"], inplace=True)
    data.reset_index(drop=True, inplace=True)

    data.sort_values('datetime', inplace = True)
    data.to_pickle(output_filepath)

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../0-raw/zip) into
        serialized data ready to be used in Pandas (saved in ../1-import).
    """
    logger = logging.getLogger(__file__)
    logger.info(f'making data set from {input_filepath}')

    get_zip_data(input_filepath, output_filepath)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    main()