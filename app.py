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
top_100_symbols = [
    'ACE', 'ADVANC', 'AMATA', 'AOT', 'AP', 'AWC', 'BAM', 'BANPU', 'BBL', 'BCH', 'BCP', 'BCPG',
    'BDMS', 'BEC', 'BEM', 'BGRIM', 'BH', 'BLA', 'BTS', 'BYD', 'CBG', 'CENTEL', 'CHG', 'CK',
    'CKP', 'COM7', 'CPALL', 'CPF', 'CPN', 'CRC', 'DELTA', 'DOHOME', 'EA', 'EGCO', 'EPG', 'ESSO',
    'FORTH', 'GLOBAL', 'GPSC', 'GULF', 'GUNKUL', 'HANA', 'HMPRO', 'INTUCH', 'IRPC', 'IVL',
    'JAS', 'SET', 'JMART', 'JMT', 'KBANK', 'KCE', 'KEX', 'KKP', 'KTB', 'KTC', 'LH', 'MEGA', 'MINT',
    'MTC', 'NEX', 'ONEE', 'OR', 'ORI', 'OSP', 'PLANB', 'PSL', 'PTG', 'PTT', 'PTTEP', 'PTTGC', 'QH',
    'RATCH', 'RBF', 'RCL', 'SABUY', 'SAWAD', 'SCB', 'SCC', 'SCGP', 'SINGER', 'SIRI', 'SJWD',
    'SPALI', 'SPRC', 'STA', 'STGT', 'TCAP', 'THANI', 'THG', 'TIDLOR', 'TIPH', 'TISCO', 'TOP',
    'TQM', 'TRUE', 'TTB', 'TU', 'VGI', 'WHA'
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
n_bars = 400
#Generating Colors For Histogram
def gen_macd_color(df):
    macd_color = []
    macd_color.clear()
    for i in range (0,len(df["MACDh_12_26_9"])):
        if df["MACDh_12_26_9"][i] >= 0 and df["MACDh_12_26_9"][i-1] < df["MACDh_12_26_9"][i]:
            macd_color.append('#26A69A')
            #print(i,'green')
        elif df["MACDh_12_26_9"][i] >= 0 and df["MACDh_12_26_9"][i-1] > df["MACDh_12_26_9"][i]:
            macd_color.append('#B2DFDB')
            #print(i,'faint green')
        elif df["MACDh_12_26_9"][i] < 0 and df["MACDh_12_26_9"][i-1] > df["MACDh_12_26_9"][i] :
            #print(i,'red')
            macd_color.append('#FF5252')
        elif df["MACDh_12_26_9"][i] < 0 and df["MACDh_12_26_9"][i-1] < df["MACDh_12_26_9"][i] :
            #print(i,'faint red')
            macd_color.append('#FFCDD2')
        else:
            macd_color.append('#000000')
            #print(i,'no')
    return macd_color
plot = False
for symbol in top_100_symbols:
    try:
        print(f'Getting data for {symbol}')
        idf = tv.get_hist(symbol=symbol, exchange='set', interval=interval, n_bars=n_bars)
        df = idf.copy()
        df.index.name = 'Date'
        
       
        
        # Calculate CDC action zones
        df['ema_short'] = df.close.ewm(span=12, adjust=False, min_periods=12).mean()
        df['ema_long'] = df.close.ewm(span=26, adjust=False, min_periods=26).mean()
        df['trend'] = df['ema_short'] > df['ema_long']
        df.loc[(df.trend == True) & (df.trend.shift() == False), 'action'] = 'buy'
        df.loc[(df.trend == False) & (df.trend.shift() == True), 'action'] = 'sell'
        df.loc[df['action'] == 'buy', 'marker_position'] = df['low'] * 0.95
        df.loc[df['action'] == 'sell', 'marker_position'] = df['high'] * 1.05
         # Save the data to a CSV file
        csv_filename = os.path.join(output_folder, f'{symbol}_processed_data.csv')
        df.to_csv(csv_filename)
        print(f'Calculating indicators for {symbol}')
        # Get the 26-day EMA of the closing price
        k = df['close'].ewm(span=12, adjust=False, min_periods=12).mean()

        # Get the 12-day EMA of the closing price
        d = df['close'].ewm(span=26, adjust=False, min_periods=26).mean()

        # Subtract the 26-day EMA from the 12-Day EMA to get the MACD
        macd = k - d

        # Get the 9-Day EMA of the MACD for the Trigger line
        macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()

        # Calculate the difference between the MACD - Trigger for the Convergence/Divergence value
        macd_h = macd - macd_s
        # Add all of our new values for the MACD to the dataframe
        df['MACD_12_26_9'] = df.index.map(macd)
        df['MACDh_12_26_9'] = df.index.map(macd_h)
        df['MACDs_12_26_9'] = df.index.map(macd_s)
        
        macd = df[['MACD_12_26_9']]
        histogram = df[['MACDh_12_26_9']]
        signal = df[['MACDs_12_26_9']]
        macd_color = gen_macd_color(df)


        apds = [
            mpf.make_addplot(macd,color='#2962FF', panel=1),
            mpf.make_addplot(signal,color='#FF6D00', panel=1),
            mpf.make_addplot(histogram,type='bar',width=0.7,panel=1, color=macd_color,alpha=1,secondary_y=True),
         ]
        if plot :
            mpf.plot(
                df,
                title=symbol,
                volume=True,
                type="candle", 
                style="yahoo",
                addplot=apds,
                volume_panel=2,
                figsize=(20,10)
            )
        print(f'Plot for {symbol} completed\n')
    except Exception as e:
        print(f'Error processing {symbol}: {e}')
        print(f'Skipping {symbol}\n')

print("Data retrieval, CSV saving, and plotting complete.")
