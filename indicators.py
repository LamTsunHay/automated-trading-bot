from textwrap import indent
import pandas as pd
from utils import * 

SYMBOL = 'EURUSD'

df = pd.read_csv(f'data/csv/{SYMBOL}.csv')
df['FastSMA'] = df['Close'].rolling(7, min_periods=7).mean().fillna(df['Close'])
df['SlowSMA'] = df['Close'].rolling(20, min_periods=20).mean().fillna(df['Close'])
df['RSI'] = rsi(df)
df.dropna(inplace=True)
df.reset_index(drop=True, inplace=True)

class Indicators:

    def get_df(self):
        return df

    def get_volume(self, time):
        return df['Volume'].iloc[time]

    def get_close_price(self, time):
        return df['Close'].iloc[time]

    def trend(self, time, lookback=10):
        if time < lookback:
            return 0
        return sigmoid((df['Close'].iloc[time - lookback] - df['Close'].iloc[time]) / lookback)

    def price_diff_with_prev(self, time):
        if time<1:return 0
        return ((df['Close'].iloc[time] - df['Close'].iloc[time-1]) / df['Close'].iloc[time-1])

    def get_rsi(self, time):
        return df['RSI'].iloc[time]

    def get_sma_diff_pct(sefl, time):
        return (df['FastSMA'].iloc[time] - df['SlowSMA'].iloc[time]) / df['SlowSMA'].iloc[time]


  
    