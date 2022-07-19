from numpy import rec
import plotly.graph_objects as go
import pandas as pd

SYMBOL = 'EURUSD'
MODE = 'test'


def visualise():
    df = pd.read_csv(f'data/csv/_{SYMBOL}_{MODE}.csv')
    df = df.set_index(pd.DatetimeIndex(df['Unnamed: 0'].values))
    df.drop(df[df.Volume == 0].index, inplace=True)

    record = pd.read_csv(f'result/{SYMBOL}_result.csv')
    buy = record.drop(record[record.Type != 'Buy'].index)
    sell = record.drop(record[record.Type != 'sell'].index)
    close = record.drop(record[record.Type != 'Close'].index)

    figure = go.Figure(
        data=[
            go.Candlestick(
                name='Candlestick',
                x=df.index,
                low=df['Low'],
                high=df['High'],
                close=df['Close'],
                open=df['Open'],
                increasing_line_color='green',
                decreasing_line_color='red'
            ),
            go.Scatter(
                name='Buy',
                marker=dict(size=14, line=dict(width=2, color='DarkSlateGrey')),
                line=dict(width=0),
                y=buy['Price'],
                x=buy['Index'],
            ),
            go.Scatter(
                name='Sell',
                marker=dict(size=14, line=dict(width=2, color='DarkSlateGrey')),
                line=dict(width=0),
                y=sell['Price'],
                x=sell['Index'],
            ),
            go.Scatter(
                name='Close',
                marker=dict(size=13, line=dict(width=2, color='DarkSlateGrey')),
                line=dict(width=0),
                y=close['Price'],
                x=close['Index'],
            ),
        ]
    )

    figure.show()
