#import libraries
import pandas as pd
import os

# Specify path to excel file in project folder
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
file_path = os.path.join(script_dir, '../../data/data_source_final.xlsx') #<-- dir the data file is in --remove a /.. when moving script to scripts folder

# Read in the excel file
all_sheets = pd.read_excel(file_path, sheet_name=None)

print(all_sheets.keys())

