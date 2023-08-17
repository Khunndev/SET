import pandas as pd
import numpy as np

# Load your OHLC data into a DataFrame (assuming you have columns: 'close', 'high', 'low')
# df = pd.read_csv('path_to_your_data.csv')

# Calculate moving averages
sma50 = df['close'].rolling(window=50).mean()
sma150 = df['close'].rolling(window=150).mean()
sma200 = df['close'].rolling(window=200).mean()
sma200_22 = sma200.shift(22)

# Define the criteria functions
def is_price_above_sma_150_and_200():
    return (df['close'] > sma150) & (df['close'] > sma200)

def is_sma_150_above_sma_200():
    return sma150 > sma200

def is_trending_at_least_1_month():
    return sma200 > sma200_22

def is_sma_50_above_sma_150_and_200():
    return (sma50 > sma150) & (sma50 > sma200)

def is_current_price_above_ma_50():
    return df['close'] > sma50

def is_price_25_percent_above_52_weeks_low():
    highest_price = df['high'].rolling(window=260).max()
    lowest_price = df['low'].rolling(window=260).min()
    return ((df['close'] / lowest_price) - 1) * 100 >= 25

def is_price_within_52_high():
    return (1 - (df['close'] / highest_price)) * 100 <= 25

def is_rs_rating_more_than_seventy():
    three_month_rs = 0.4 * (df['close'] / df['close'].shift(13))
    six_month_rs = 0.2 * (df['close'] / (df['close'].shift(26) * 2))
    nine_month_rs = 0.2 * (df['close'] / (df['close'].shift(39) * 3))
    twelve_month_rs = 0.2 * (df['close'] / (df['close'].shift(52) * 4))
    rs_rating = (three_month_rs + six_month_rs + nine_month_rs + twelve_month_rs) * 100
    return rs_rating > 70

# Apply the criteria functions
df['is_price_above_sma_150_and_200'] = is_price_above_sma_150_and_200()
df['is_sma_150_above_sma_200'] = is_sma_150_above_sma_200()
df['is_trending_at_least_1_month'] = is_trending_at_least_1_month()
df['is_sma_50_above_sma_150_and_200'] = is_sma_50_above_sma_150_and_200()
df['is_current_price_above_ma_50'] = is_current_price_above_ma_50()
df['is_price_25_percent_above_52_weeks_low'] = is_price_25_percent_above_52_weeks_low()
df['is_price_within_52_high'] = is_price_within_52_high()
df['is_rs_rating_more_than_seventy'] = is_rs_rating_more_than_seventy()

# Calculate the meet_all_criteria column
df['is_meet_all_criteria'] = df[
    ['is_price_above_sma_150_and_200', 'is_sma_150_above_sma_200', 'is_trending_at_least_1_month',
     'is_sma_50_above_sma_150_and_200', 'is_price_25_percent_above_52_weeks_low', 
     'is_price_within_52_high', 'is_rs_rating_more_than_seventy', 'is_current_price_above_ma_50']
].all(axis=1)

# Count the number of criteria met
df['count'] = df[
    ['is_price_above_sma_150_and_200', 'is_sma_150_above_sma_200', 'is_trending_at_least_1_month',
     'is_sma_50_above_sma_150_and_200', 'is_price_25_percent_above_52_weeks_low', 
     'is_price_within_52_high', 'is_rs_rating_more_than_seventy', 'is_current_price_above_ma_50']
].sum(axis=1)

# Print the DataFrame or save to a CSV file
print(df)
# df.to_csv('minervini_results.csv')
