import numpy as np


def MACD(DataFrame, fma=12, sma=26, n=9):
    """
    Calculate the Moving Average Convergence Divergence
    
    Input:
    The price DataFrame
    fma - fast moving average
    sma - slow moving average
    n - period of moving average of the signal line 
    """
    df = DataFrame.copy()
    df["MA_fast"] = df["Close"].ewm(span=fma, min_periods=fma).mean()
    df["MA_slow"] = df["Close"].ewm(span=sma, min_periods=sma).mean()
    df["MACD"] = df["MA_fast"] - df["MA_slow"]
    df["MACD_signal"] = df["MACD"].ewm(span=n, min_periods=n).mean()
    df.dropna(inplace=True)
    return df


def BB(DataFrame, n=20, m=2):
    """
    Calculate the Bollinger Band

    Input:
    The price DataFrame
    n - period of moving averagen
    m - umber of standard deviation above/below
    """
    df = DataFrame.copy()
    df["MA"] = df["Close"].ewm(span=n, min_periods=n).mean()
    df["BB_up"] = df["MA"] + m * df["Close"].rolling(n).std(ddof=0)
    df["BB_down"] = df["MA"] - m * df["Close"].rolling(n).std(ddof=0)
    df["BB_width"] = df["BB_up"] - df["BB_down"]
    df.dropna(inplace=True)
    return df


def ATR(DataFrame, n=20):
    """
    Calculate the Average True Range
    
    Input:
    The price DataFrame
    n - period of moving average of the True Range 
    """
    df = DataFrame.copy()
    df["H-L"] = abs(df["High"] - df["Low"])
    df["H-PC"] = abs(df["High"] - df["Close"].shift(1))
    df["L-PC"] = abs(df["Low"] - df["Close"].shift(1))
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    df["ATR"] = df["TR"].ewm(span=n, min_periods=n).mean()
    return df["ATR"]


def RSI(DataFrame, n=20):
    """
    Calculate the Relative Strengh Indes

    Input:
    The price DataFrame
    n - period of the RSI
    """
    df = DataFrame.copy()
    df["delta"] = df["Close"] - df["Close"].shift(1)
    df["gain"] = np.where(df["delta"] >= 0, df["delta"], 0)
    df["loss"] = np.where(df["delta"] < 0, abs(df["delta"]), 0)
    avg_gain = []
    avg_loss = []
    gain = df["gain"].tolist()
    loss = df["loss"].tolist()
    for i in range(len(df)):
        if i < n:
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == n:
            avg_gain.append(df["gain"].rolling(n).mean()[n])
            avg_loss.append(df["loss"].rolling(n).mean()[n])
        elif i > n:
            avg_gain.append(((n - 1) * avg_gain[i - 1] + gain[i]) / n)
            avg_loss.append(((n - 1) * avg_loss[i - 1] + loss[i]) / n)
    df["avg_gain"] = np.array(avg_gain)
    df["avg_loss"] = np.array(avg_loss)
    df["RS"] = df["avg_gain"] / df["avg_loss"]
    df["RSI"] = 100 - (100 / (1 + df["RS"]))
    return df["RSI"]


def ADX(DataFrame, n=20):
    """
    Calculate the Average Directional Index
    
    Input:
    The price DataFrame
    n - period of the ADX
    """
    df = DataFrame.copy()
    df["H-L"] = abs(df["High"] - df["Low"])
    df["H-PC"] = abs(df["High"] - df["Close"].shift(1))
    df["L-PC"] = abs(df["Low"] - df["Close"].shift(1))
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    df["+DM"] = np.where(
        (df["High"] - df["High"].shift(1)) > (df["Low"].shift(1) - df["Low"]),
        df["High"] - df["High"].shift(1),
        0,
    )
    df["+DM"] = np.where(df["+DM"] < 0, 0, df["+DM"])
    df["-DM"] = np.where(
        (df["Low"].shift(1) - df["Low"]) > (df["High"] - df["High"].shift(1)),
        df["Low"].shift(1) - df["Low"],
        0,
    )
    df["-DM"] = np.where(df["-DM"] < 0, 0, df["-DM"])
    df["+DMMA"] = df["+DM"].ewm(span=n, min_periods=n).mean()
    df["-DMMA"] = df["-DM"].ewm(span=n, min_periods=n).mean()
    df["TRMA"] = df["TR"].ewm(span=n, min_periods=n).mean()
    df["+DI"] = 100 * (df["+DMMA"] / df["TRMA"])
    df["-DI"] = 100 * (df["-DMMA"] / df["TRMA"])
    df["DX"] = 100 * (abs(df["+DI"] - df["-DI"]) / (df["+DI"] + df["-DI"]))
    df["ADX"] = df["DX"].ewm(span=n, min_periods=n).mean()
    return df["ADX"]


def SO(DataFrame, l=20, n=3):
    """
    Calculate the Stochastics Oscillator
    
    Input:
    The price DataFrame
    l - period of lookback 
    n = period of moving average for %D
    """
    df = DataFrame.copy()
    df["C-L"] = df["Close"] - df["Low"].rolling(l).min()
    df["H-L"] = df["High"].rolling(l).max() - df["Low"].rolling(l).min()
    df["%K"] = df["C-L"] / df["H-L"] * 100
    df["%D"] = df["%K"].ewm(span=n, min_periods=n).mean()
    return df["%D"]
