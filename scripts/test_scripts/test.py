#import libraries
import pandas as pd
import os

def process_df_list(dataframes):
    """
    Function to process a list of dataframes.

    Args: dataframes (list): list of dataframes to process

    Returns: None
    """
    for df in dataframes:
        print(df.info())
        print(df.head())

# Specify path to excel file in project folder
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
file_path = os.path.join(script_dir, '../../data/data_source_final.xlsx') #<-- dir the data file is in --remove a /.. when moving script to scripts folder

# Read in the excel file
all_sheets = pd.read_excel(file_path, sheet_name=None)

# test that the excel sheet is loaded --> print(all_sheets.keys())

# load the data sheets from excel as data frames
market_mapping_df = all_sheets['market_mapping']
asset_oec_df = all_sheets['asset_oec']
rentals_df = all_sheets['rentals']

# create a list of unprocessed dataframes -- REFERENCE ONLY
df_list = [market_mapping_df, asset_oec_df, rentals_df]

# cleaning asset oec data
filt_asset_oec_df = asset_oec_df[asset_oec_df['market_id'].isin(market_mapping_df['market_id'])]
print(filt_asset_oec_df.duplicated().sum())


# process_df_list(df_list)



