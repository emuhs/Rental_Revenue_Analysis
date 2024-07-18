#import libraries
import pandas as pd
import os
import matplotlib.pyplot as plt
from tabulate import tabulate
import statsmodels.api as sm
import seaborn as sns
from scipy.stats import norm

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
fm_source_df = fm_source_df[fm_source_df['rental_revenue']>1]

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
plt.title('Rental Revenue Ratios by Asset Category Across Markets')
plt.legend(title='Asset Category')
plt.grid(True)
plt.xticks(rotation=0)
plt.tight_layout()

# save the plot
plt.savefig('../figures/market_rental_revenue_ratios_by_asset_category.png')

""" Step 5 - Calculate the time utilization by asset class.  Calculate the financial utilization as Financial Utilization = (Annualized Revenue)/OEC for each market and plot the results.  Save the plot to a new file in the figures folder."""
# determine distinct assets and their OEC using the filtered and merged source dataframe
asset_distinct_source_df = fm_source_df[['market_id','asset_id','oec','equipment_class']].drop_duplicates(subset=['asset_id'], keep='first')
time_utilization_by_asset = fm_source_df.groupby(['market_id','asset_id','equipment_class'])['rental_date'].count().reset_index()
time_utilization_by_asset['time_utilization'] = time_utilization_by_asset['rental_date']/12
time_utilization_by_equipment_class = time_utilization_by_asset.groupby(['market_id','equipment_class'])['time_utilization'].mean().unstack().reset_index()

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
market_utilization_df['aerial_time_utilization'] = time_utilization_by_equipment_class['Aerial']
market_utilization_df['dirt_time_utilization'] = time_utilization_by_equipment_class['Dirt']

util_order = ['market_id','aerial_time_utilization','aerial_financial_utilization','dirt_time_utilization','dirt_financial_utilization','total_financial_utilization']

market_utilization_df = market_utilization_df[util_order]

market_utilization_df.to_excel('../data/market_utilization_df.xlsx', index=False)

# calculate the cdf of the market utilization metrics
market_utilization_cdf = market_utilization_df.copy()
for column in market_utilization_cdf.columns[1:]:
    market_utilization_cdf[column] = norm.cdf(market_utilization_cdf[column], market_utilization_cdf[column].mean(), market_utilization_cdf[column].std())

# set the index of the cdf dataframe
market_utilization_cdf.set_index('market_id', inplace=True)

# create a heatmap of the cdf dataframe
plt.figure(figsize=(10,10))
sns.heatmap(market_utilization_cdf, cmap='RdYlGn', annot=True, fmt=".2f")
plt.title('Heatmap of Normally Distributed Utilization Metrics')
plt.xlabel('Utilization Metrics')
plt.ylabel('Market ID')
plt.tight_layout()
plt.show()


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

""" Step 6 - Analyze Equipment distribution by market """
# group by market_id and equipment_class and count the number of assets
grouped_asset_distinct_source_df = asset_distinct_source_df.groupby(['market_id','equipment_class'])['asset_id'].count().unstack()

# plot the grouped data
grouped_asset_distinct_source_df.plot(kind='bar')

# add labels and title
plt.xlabel('Market ID')
plt.ylabel('Number of Assets')
plt.title('Equipment Distribution by Market')
plt.legend(title='Asset Category')
plt.grid(True)
plt.xticks(rotation=0)
plt.tight_layout()

# save the plot
plt.savefig('../figures/equipment_distribution_by_market.png')


""" Step 7 - Correlate financial utilization and revenue with equipment distribution by market """
# merge the financial utilization and equipment distribution dataframes
utilization_distribution_df = pd.merge(market_utilization_df, grouped_asset_distinct_source_df, on='market_id', how='inner')
utilization_distribution_df['aerial_pct'] = utilization_distribution_df['Aerial'] / (utilization_distribution_df['Aerial']+utilization_distribution_df['Dirt'])
utilization_distribution_df['dirt_pct'] = utilization_distribution_df['Dirt'] / (utilization_distribution_df['Aerial']+utilization_distribution_df['Dirt'])

# plot the counted distribution vs financial utilization
utilization_distribution_df.plot(kind='scatter', x='Dirt', y='dirt_financial_utilization', color='red', label='Dirt')
utilization_distribution_df.plot(kind='scatter', x='Aerial', y='aerial_financial_utilization', color='blue', label='Aerial', ax=plt.gca())

# add labels and title
plt.xlabel('Asset Count')
plt.ylabel('Financial Utilization')
plt.title('Financial Utilization vs Equipment Distribution')
plt.legend(title='Asset Category')
plt.grid(True)
plt.xticks(rotation=0)

# save the plot
plt.savefig('../figures/financial_utilization_vs_equipment_distribution.png')

# plot percentage distribution vs financial utilization
utilization_distribution_df.plot(kind='scatter', x='dirt_pct', y='dirt_financial_utilization', color='red', label='Dirt')
utilization_distribution_df.plot(kind='scatter', x='aerial_pct', y='aerial_financial_utilization', color='blue', label='Aerial', ax=plt.gca())

# add labels and title
plt.xlabel('Asset Percentage')
plt.ylabel('Financial Utilization')
plt.title('Financial Utilization vs Percentage Equipment Distribution')
plt.legend(title='Asset Category')
plt.grid(True)
plt.xticks(rotation=0)

# save the plot
plt.savefig('../figures/financial_utilization_vs_percentage_equipment_distribution.png')

# incorporate the equipment distribution into the annual market revenue dataframe
annual_market_revenue_df['Aerial'] = utilization_distribution_df['Aerial']
annual_market_revenue_df['Dirt'] = utilization_distribution_df['Dirt']
annual_market_revenue_df['aerial_pct'] = utilization_distribution_df['aerial_pct']
annual_market_revenue_df['dirt_pct'] = utilization_distribution_df['dirt_pct']

# plot the counted distribution vs annual revenue
annual_market_revenue_df.plot(kind='scatter', x='Dirt', y='rental_revenue_dirt', color='red', label='Dirt')
annual_market_revenue_df.plot(kind='scatter', x='Aerial', y='rental_revenue_aerial', color='blue', label='Aerial', ax=plt.gca())

# add labels and title
plt.xlabel('Asset Count')
plt.ylabel('Annual Revenue')
plt.title('Annual Revenue vs Equipment Distribution')
plt.legend(title='Asset Category')
plt.grid(True)
plt.xticks(rotation=0)

# save the plot
plt.savefig('../figures/annual_revenue_vs_equipment_distribution.png')

# plot percentage distribution vs annual revenue
annual_market_revenue_df.plot(kind='scatter', x='dirt_pct', y='rental_revenue_dirt', color='red', label='Dirt')
annual_market_revenue_df.plot(kind='scatter', x='aerial_pct', y='rental_revenue_aerial', color='blue', label='Aerial', ax=plt.gca())

# add labels and title
plt.xlabel('Asset Percentage')
plt.ylabel('Annual Revenue')
plt.title('Annual Revenue vs Percentage Equipment Distribution')
plt.legend(title='Asset Category')
plt.grid(True)
plt.xticks(rotation=0)

# save the plot
plt.savefig('../figures/annual_revenue_vs_percentage_equipment_distribution.png')

""" Step 8 - Conduct a regression analysis  """

# prepare equipment mix by market
# asset %
asset_pct_by_market_df = grouped_asset_distinct_source_df.copy()
asset_pct_by_market_df['total_assets'] = asset_pct_by_market_df['Aerial'] + asset_pct_by_market_df['Dirt']
asset_pct_by_market_df['aerial_pct'] = asset_pct_by_market_df['Aerial'] / asset_pct_by_market_df['total_assets']
asset_pct_by_market_df['dirt_pct'] = asset_pct_by_market_df['Dirt'] / asset_pct_by_market_df['total_assets']
asset_pct_by_market_df = asset_pct_by_market_df[['aerial_pct','dirt_pct']]

# revenue by class
revenue_by_class = grouped_fm_source_df.copy()
revenue_by_class = revenue_by_class.rename(columns={'Aerial':'revenue_aerial','Dirt':'revenue_dirt'}    )

# utilization by class
oec_by_class = asset_distinct_source_df.copy()
oec_by_class = oec_by_class[['market_id','equipment_class','oec']]
oec_by_class = oec_by_class.groupby(['market_id','equipment_class'])['oec'].sum().unstack()
utilization_by_class = grouped_fm_source_df / oec_by_class
utilization_by_class = utilization_by_class.rename(columns={'Aerial':'utilization_aerial','Dirt':'utilization_dirt'})

results_df = pd.merge(asset_pct_by_market_df, revenue_by_class, on=['market_id'], how='inner')
results_df = pd.merge(results_df, utilization_by_class, on=['market_id'], how='inner')
results_df = pd.merge(grouped_asset_distinct_source_df, results_df, on=['market_id'], how='inner')
results_df = results_df.rename(columns={'Aerial':'aerial_count','Dirt':'dirt_count'})

# define function to run and save regression results
def run_regression(X, y, filename):
    X = sm.add_constant(X)
    model = sm.OLS(y, X).fit()
    with open(filename, 'w') as f:
        f.write(model.summary().as_text())

# define independent variables
X_pct = results_df[['aerial_pct']]
X_count = results_df[['aerial_count', 'dirt_count']]

# list of dependent variables and their corresponding filenames
dependent_vars = [
    ('utilization_aerial', 'ap_utilization_aerial_regression_results.txt'),
    ('utilization_dirt', 'ap_utilization_dirt_regression_results.txt'),
    ('utilization_combined', 'ap_utilization_combined_regression_results.txt', results_df['utilization_aerial'] + results_df['utilization_dirt']),
    ('revenue_aerial', 'ap_revenue_aerial_regression_results.txt'),
    ('revenue_dirt', 'ap_revenue_dirt_regression_results.txt'),
    ('revenue_combined', 'ap_revenue_combined_regression_results.txt', results_df['revenue_aerial'] + results_df['revenue_dirt'])
]

# loop through the dependent variables for percentage-based analysis
for var, filename in dependent_vars[:2] + dependent_vars[3:5]:
    y = results_df[var]
    run_regression(X_pct, y, f'../results/{filename}')

# handle combined utilization and combined revenue separately
run_regression(X_pct, dependent_vars[2][2], f'../results/{dependent_vars[2][1]}')
run_regression(X_pct, dependent_vars[5][2], f'../results/{dependent_vars[5][1]}')

# list of dependent variables and their corresponding filenames for count-based analysis
dependent_vars_count = [
    ('utilization_aerial', 'ac_utilization_aerial_regression_results.txt'),
    ('utilization_dirt', 'ac_utilization_dirt_regression_results.txt'),
    ('utilization_combined', 'ac_utilization_combined_regression_results.txt', results_df['utilization_aerial'] + results_df['utilization_dirt']),
    ('revenue_aerial', 'ac_revenue_aerial_regression_results.txt'),
    ('revenue_dirt', 'ac_revenue_dirt_regression_results.txt'),
    ('revenue_combined', 'ac_revenue_combined_regression_results.txt', results_df['revenue_aerial'] + results_df['revenue_dirt'])
]

# loop through the dependent variables for count-based analysis
for var, filename in dependent_vars_count[:2] + dependent_vars_count[3:5]:
    y = results_df[var]
    run_regression(X_count, y, f'../results/{filename}')

# handle combined utilization and combined revenue separately
run_regression(X_count, dependent_vars_count[2][2], f'../results/{dependent_vars_count[2][1]}')
run_regression(X_count, dependent_vars_count[5][2], f'../results/{dependent_vars_count[5][1]}')



















