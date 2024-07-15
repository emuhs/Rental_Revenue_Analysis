#import libraries
import pandas as pd
import os
import matplotlib.pyplot as plt

"""Step 1 - Read the excel file and load the data sheets into separate dataframes"""
# specify path to excel source file in project folder
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
file_path = os.path.join(script_dir, '../data/data_source_final.xlsx')

# read the excel file
all_sheets = pd.read_excel(file_path, sheet_name=None)

# load the data sheets from excel file into separate dataframes
market_mapping_df = all_sheets['market_mapping']
asset_oec_df = all_sheets['asset_oec']
# asset_oec_df.drop_duplicates(subset=['asset_id'], keep='first', inplace=True)
rentals_df = all_sheets['rentals']
# a key assumption in this calculation is that 
"""Step 2 - Filter the data, merge the dataframes, and save the modified source dataframe to an excel file."""
# merge the dataframes (market_mapping and asset_oec) on market_id; then merge the resulting dataframe with rentals_df on asset_id and market_id
mm_asset_merged_df = pd.merge(market_mapping_df, asset_oec_df, on=['market_id'], how='inner')
mm_asset_rental_merged_df = pd.merge(mm_asset_merged_df, rentals_df, on=['asset_id','market_id'])

# filter out entries where rental_date is after acquisition_date
acq_filt_merged_df = mm_asset_rental_merged_df[mm_asset_rental_merged_df['rental_date'] >= mm_asset_rental_merged_df['acquisition_date']]
# filter out entries where rental_date is before market_open_date
fm_source_df = acq_filt_merged_df[acq_filt_merged_df['rental_date'] >= acq_filt_merged_df['market_open_date']]

# save the filtered and merged dataframe to an excel file
fm_source_df.to_excel('../data/filt_merged_source_df.xlsx', index=False)

"""Step 3 - Initial analysis and plot of rental revenue by asset category across markets.  Save the plot to a new file in the figures folder."""
# group by equipment_class and sum rental_revenue
grouped_fm_source_df = fm_source_df.groupby(['market_id','equipment_class'])['rental_revenue'].sum().unstack()

# plot the grouped data
grouped_fm_source_df.plot(kind='bar')

# add labels and title
plt.xlabel('Market ID')
plt.ylabel('Rental Revenue')
plt.title('Rental Revenue by Asset Category Across Markets')
plt.legend(title='Asset Cagegory')
plt.grid(True)
plt.xticks(rotation=0)
plt.tight_layout()

# save the plot
plt.savefig('../figures/market_rental_revenue_by_asset_category.png')

# show the plot
plt.show()

"""Step 4 - Calculate the market ratios of aerial and dirt revenue to total revenue and plot the results.  Save the plot to a new file in the figures folder."""
# create dataframes for annual aerial and dirt revenue
annual_dirt_revenue = fm_source_df[fm_source_df['equipment_class'] == 'Dirt'].groupby('market_id')['rental_revenue'].sum().reset_index()
annual_aerial_revenue = fm_source_df[fm_source_df['equipment_class'] == 'Aerial'].groupby('market_id')['rental_revenue'].sum().reset_index()

# merge the dirt and aerial dataframes
annual_market_revenue_df = pd.merge(annual_aerial_revenue, annual_dirt_revenue, on='market_id', suffixes=('_aerial','_dirt'), how='outer')

# calculate total annual revenue
annual_market_revenue_df['total_revenue'] = annual_market_revenue_df['rental_revenue_aerial'] + annual_market_revenue_df['rental_revenue_dirt']

# initialize a new data frame calculate the market ratios of aerial and dirt revenue to total revenue
market_ratio_df = annual_market_revenue_df.copy()
market_ratio_df['aerial_ratio'] = market_ratio_df['rental_revenue_aerial']/market_ratio_df['total_revenue']
market_ratio_df['dirt_ratio'] = market_ratio_df['rental_revenue_dirt']/market_ratio_df['total_revenue']
market_ratio_df = market_ratio_df[['market_id','aerial_ratio','dirt_ratio']]

# plot the merged dataframe
market_ratio_df.plot(kind='bar', x='market_id')

# add labels and title
plt.xlabel('Market ID')
plt.ylabel('Rental Revenue Ratio')
plt.title('Rental Revenue Ratios by Equipment Class Across Markets')
plt.legend(title='Equipment Class')
plt.grid(True)
plt.xticks(rotation=0)
plt.tight_layout()

# save the plot
plt.savefig('../figures/market_rental_revenue_ratios_by_asset_category.png')

# show the plot
plt.show()

""" Step 5 - Calculate the financial utilization as Financial Utilization = (Annualized Revenue)/OEC for each market and plot the results.  Save the plot to a new file in the figures folder."""
# determine distinct assets and their OEC using the filtered and merged source dataframe
asset_distinct_source_df = fm_source_df[['market_id','asset_id','oec','equipment_class']].drop_duplicates(subset=['asset_id'], keep='first')

# calculate the total oec by asset category and market
total_dirt_oec = asset_distinct_source_df[asset_distinct_source_df['equipment_class'] == 'Dirt'].groupby('market_id')['oec'].sum().reset_index()
total_aerial_oec = asset_distinct_source_df[asset_distinct_source_df['equipment_class'] == 'Aerial'].groupby('market_id')['oec'].sum().reset_index()

# merge the dirt and aerial dataframes
total_oec_df = pd.merge(total_aerial_oec, total_dirt_oec, on='market_id', suffixes=('_aerial','_dirt'), how='outer')

# calculate the total oec by market
total_oec_df['total_oec'] = total_oec_df['oec_aerial'] + total_oec_df['oec_dirt']

# calculate financial utilization by market and asset category, and combine the results into a single dataframe
market_utilization_df = total_oec_df.copy()
market_utilization_df['aerial_financial_utilization'] = annual_market_revenue_df['rental_revenue_aerial']/market_utilization_df['oec_aerial']
market_utilization_df['dirt_financial_utilization'] = annual_market_revenue_df['rental_revenue_dirt']/market_utilization_df['oec_dirt']
market_utilization_df['total_financial_utilization'] = annual_market_revenue_df['total_revenue']/market_utilization_df['total_oec']
market_utilization_df = market_utilization_df[['market_id','aerial_financial_utilization','dirt_financial_utilization','total_financial_utilization']]

# plot the merged dataframe
market_utilization_df.plot(kind='bar', x='market_id')

# add labels and title
plt.xlabel('Market ID')
plt.ylabel('Financial Utilization')
plt.title('Financial Utilization by Asset Category Across Markets')
plt.legend(title='Asset Category')
plt.grid(True)
plt.xticks(rotation=0)
plt.tight_layout()

# save the plot
plt.savefig('../figures/market_financial_utilization_by_asset_category.png')

# show the plot
plt.show()



























