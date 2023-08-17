import os
import csv
import pandas as pd
import pandas_ta as ta
import mplfinance as mpf
import numpy as np
from tvDatafeed import TvDatafeed, Interval

# Create a folder to store CSV files if it doesn't exist
output_folder = 'ohlc_data'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Initialize TvDatafeed
tv = TvDatafeed()

# Get the top 100 Thai SET symbols (Replace this list with the actual symbols)
# Get the top 100 Thai SET symbols (Replace this list with the actual symbols)
top_100_symbols = [
    'ACE', 'ADVANC', 'AMATA', 'AOT', 'AP', 'AWC', 'BAM', 'BANPU', 'BBL', 'BCH', 'BCP', 'BCPG',
    'BDMS', 'BEC', 'BEM', 'BGRIM', 'BH', 'BLA', 'BTS', 'BYD', 'CBG', 'CENTEL', 'CHG', 'CK',
    'CKP', 'COM7', 'CPALL', 'CPF', 'CPN', 'CRC', 'DELTA', 'DOHOME', 'EA', 'EGCO', 'EPG', 'ESSO',
    'FORTH', 'GLOBAL', 'GPSC', 'GULF', 'GUNKUL', 'HANA', 'HMPRO', 'INTUCH', 'IRPC', 'IVL',
    'JAS', 'SET', 'JMART', 'JMT', 'KBANK', 'KCE', 'KEX', 'KKP', 'KTB', 'KTC', 'LH', 'MEGA', 'MINT',
    'MTC', 'NEX', 'ONEE', 'OR', 'ORI', 'OSP', 'PLANB', 'PSL', 'PTG', 'PTT', 'PTTEP', 'PTTGC', 'QH',
    'RATCH', 'RBF', 'RCL', 'SABUY', 'SAWAD', 'SCB', 'SCC', 'SCGP', 'SINGER', 'SIRI', 'SJWD',
    'SPALI', 'SPRC', 'STA', 'STGT', 'TCAP', 'THANI', 'THG', 'TIDLOR', 'TIPH', 'TISCO', 'TOP',
    'TQM', 'TRUE', 'TTB', 'TU', 'VGI', 'WHA' , 'XO'
]
# Define the interval and number of bars
""" Interval.in_1_minute
Interval.in_3_minute
Interval.in_5_minute
Interval.in_15_minute
Interval.in_30_minute
Interval.in_45_minute
Interval.in_1_hour
Interval.in_2_hour
Interval.in_3_hour
Interval.in_4_hour
Interval.in_daily
Interval.in_weekly
Interval.in_monthly """
interval = Interval.in_daily
n_bars = 250
#Generating Colors For Histogram
plot = False
# Create a dictionary to store the first met dates for each symbol
first_met_dates = {}
for symbol in top_100_symbols:
    try:
        print(f'Getting data for {symbol}')
        idf = tv.get_hist(symbol=symbol, exchange='set', interval=interval, n_bars=n_bars)
        df = idf.copy()
        df.index.name = 'Date'
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
            highest_price = df['high'].rolling(window=260).max()
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
        
        # Filter data where is_meet_all_criteria is True
        filtered_data = df[df['is_meet_all_criteria']]

        # If there are rows that meet criteria, get the first met date
        if not filtered_data.empty:
            first_met_date = filtered_data.index[0]
            first_met_dates[symbol] = first_met_date
        # Print the DataFrame or save to a CSV file
        #print(df)
        #df_filtered = df[[ 'symbol', 'open', 'high', 'low', 'close', 'volume', 'is_meet_all_criteria', 'count']]
        #df_filtered.to_csv(f'{symbol}_minervini_results.csv')
    except Exception as e:
        print(f'Error processing {symbol}: {e}')
        print(f'Skipping {symbol}\n')

print("Data retrieval, CSV saving, and plotting complete.")
# Display symbols and their first met dates
print("Symbols where criteria were first met:")
for symbol, date in first_met_dates.items():
    print(f"Symbol: {symbol}, First Met Date: {date}")