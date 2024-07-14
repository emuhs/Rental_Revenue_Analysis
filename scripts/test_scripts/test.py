import pandas as pd
import matplotlib.pyplot as plt

# Sample data provided by the user
sample_data = {
    'asset_id': [17891.0, 17751.0, 4058.0, 4058.0, 4058.0, 4058.0, 4058.0],
    'market_id': [9.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    'acquisition_date': pd.to_datetime(['2017-11-01', '2017-11-01', '2016-01-01', '2016-01-01', '2016-01-01', '2016-01-01', '2016-01-01']),
    'equipment_class': ['Dirt', 'Aerial', 'Aerial', 'Aerial', 'Aerial', 'Aerial', 'Aerial'],
    'oec': [185400.0, 151261.2, 147600.0, 147600.0, 147600.0, 147600.0, 147600.0],
    'rental_date': pd.to_datetime(['2017-12-01', '2017-12-01', '2017-01-01', '2017-01-01', '2017-02-01', '2017-03-01', '2017-05-01']),
    'rental_id': [36645, 39999, 16052, 17712, 18382, 21270, 24435],
    'rental_revenue': [9498.3984, 1584.0, 399.1320, 900.0, 900.0, 990.0, 5855.6088]
}

df_sample = pd.DataFrame(sample_data)

# Step 1: Group by market and equipment class, summing the rental revenue
grouped = df_sample.groupby(['market_id', 'equipment_class'])['rental_revenue'].sum().reset_index()

# Step 2: Calculate total revenue per market
total_revenue_per_market = grouped.groupby('market_id')['rental_revenue'].sum().reset_index()
total_revenue_per_market.rename(columns={'rental_revenue': 'total_revenue'}, inplace=True)

# Step 3: Merge the total revenue per market back to the grouped data
merged = pd.merge(grouped, total_revenue_per_market, on='market_id')

# Step 4: Pivot the data to have columns for Aerial, Dirt, and Total Revenue
aerial_revenue = merged[merged['equipment_class'] == 'Aerial'][['market_id', 'rental_revenue']].rename(columns={'rental_revenue': 'Aerial'})
dirt_revenue = merged[merged['equipment_class'] == 'Dirt'][['market_id', 'rental_revenue']].rename(columns={'rental_revenue': 'Dirt'})
total_revenue = merged[['market_id', 'total_revenue']].drop_duplicates()

# Step 5: Combine the data into one DataFrame
revenue_data = pd.merge(aerial_revenue, dirt_revenue, on='market_id', how='outer')
revenue_data = pd.merge(revenue_data, total_revenue, on='market_id', how='outer')

# Replace NaN values with 0 (in case some markets do not have both equipment classes)
revenue_data.fillna(0, inplace=True)

# Display the result
#import ace_tools as tools; tools.display_dataframe_to_user(name="Revenue by Market", dataframe=revenue_data)

# Step 6: Plot the data
revenue_data.plot(
    x='market_id', 
    y=['Aerial', 'Dirt', 'total_revenue'], 
    kind='bar', 
    figsize=(14, 7), 
    title='Revenue by Market'
)

plt.xlabel('Market ID')
plt.ylabel('Revenue')
plt.title('Revenue from Aerial, Dirt, and Total Revenue by Market')
plt.legend(title='Revenue Type')
plt.grid(True)
plt.tight_layout()

# Save the plot to a file
#plt.savefig('/mnt/data/revenue_by_market.png')

# Display the plot
plt.show()
