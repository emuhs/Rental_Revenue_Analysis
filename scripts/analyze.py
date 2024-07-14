#import libraries
import pandas as pd
import os
import matplotlib.pyplot as plt

# Specify path to excel source file in project folder
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
file_path = os.path.join(script_dir, '../data/data_source_final.xlsx')

# Read in the excel file
all_sheets = pd.read_excel(file_path, sheet_name=None)

# load the data sheets from excel as data frames
market_mapping_df = all_sheets['market_mapping']
asset_oec_df = all_sheets['asset_oec']
rentals_df = all_sheets['rentals']

# create a list of unprocessed dataframes -- REFERENCE ONLY
unfilt_df_list = [market_mapping_df, asset_oec_df, rentals_df]

# merge the dataframes (market_mapping and asset_oec) on market_id; then merge the resulting dataframe with rentals_df on asset_id and market_id
mm_asset_merged_df = pd.merge(market_mapping_df, asset_oec_df, on=['market_id'])
mm_asset_rental_merged_df = pd.merge(mm_asset_merged_df, rentals_df, on=['asset_id','market_id'])

# filter out entries where rental_date is after acquisition_date
acq_filt_merged_df = mm_asset_rental_merged_df[mm_asset_rental_merged_df['rental_date'] >= mm_asset_rental_merged_df['acquisition_date']]
# filter out entries where rental_date is before market_open_date
fm_source_df = acq_filt_merged_df[acq_filt_merged_df['rental_date'] >= acq_filt_merged_df['market_open_date']]

#fm_source_df.to_excel('../data/filt_merged_source_df.xlsx', index=False)

# group by equipment_class and sum rental_revenue
grouped_fm_source_df = fm_source_df.groupby(['market_id','equipment_class'])['rental_revenue'].sum().unstack()

# plot the grouped data
grouped_fm_source_df.plot(kind='bar')

# add labels and title
plt.xlabel('Market ID')
plt.ylabel('Rental Revenue')
plt.title('Rental Revenue by Equipment Class Across Markets')
plt.legend(title='Equipment Class')
plt.grid(True)
plt.xticks(rotation=0)
plt.tight_layout()

# save the plot
#plt.savefig('../figures/market_rental_revenue_by_equipment_class.png')

# show the plot
#plt.show()

total_revenue_by_market = fm_source_df.groupby('market_id')['rental_revenue'].sum()
#print(total_revenue_by_market.head(10))
print(total_revenue_by_market.info())
#print(total_revenue_by_market.describe())












