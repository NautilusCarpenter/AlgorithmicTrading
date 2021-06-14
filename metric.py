import numpy as np


def Bar_Multiplier(barSize="30 mins"):
    """
    Return the corresponding multiplier for different size of data
    """
    multiplier = 1
    if barSize == "1 min":
        multiplier = 390.0
    if barSize == "2 mins":
        multiplier = 195.0
    if barSize == "3 mins":
        multiplier = 130.0
    if barSize == "5 mins":
        multiplier = 78.0
    if barSize == "10 mins":
        multiplier = 39.0
    if barSize == "15 mins":
        multiplier = 26.0
    if barSize == "20 mins":
        multiplier = 19.5
    if barSize == "30 mins":
        multiplier = 13.0
    if barSize == "1 hour":
        multiplier = 6.5
    if barSize == "2 hours":
        multiplier = 3.25
    if barSize == "3 hours":
        multiplier = 2.1666666667
    if barSize == "4 hours":
        multiplier = 1.625
    if barSize == "8 hours":
        multiplier = 0.8125
    if barSize == "1 day":
        multiplier = 1
    return multiplier


def Daily_Return(DataFrame, logReturn=True):
    """
    Calculate the daily return
    
    Input:
    The price DataFrame with the return column
    logReturn - type of the return
    """
    df = DataFrame.copy()
    if logReturn == True:
        df["Return"] = np.log(df["Close"] / df["Close"].shift(1))
    else:
        df["Return"] = df["Close"].pct_change()
    return df


def CAGR(DataFrame, logReturn=True, barSize="30 mins"):
    """
    Calculate the Cumulative Annual Growth Rate
    
    Input:
    The price DataFrame with the return column
    barSize - the bar size of the price DataFrame
    """
    df = DataFrame.copy()
    multiplier = Bar_Multiplier(barSize)
    if logReturn == True:
        cumReturn = df["Return"].cumsum()[-1]
    else:
        cumReturn = (1 + df["Return"]).cumprod()[-1] - 1
    tradingYear = len(df) / (252 * multiplier)
    CAGR = (cumReturn + 1) ** (1 / tradingYear) - 1
    return CAGR


def Volatility(DataFrame, barSize="30 mins"):
    """
    Calculate the annualised volatility
    
    Input:
    The price DataFrame with the return column
    barSize - the bar size of the price DataFrame
    """
    df = DataFrame.copy()
    multiplier = Bar_Multiplier(barSize)
    volatility = df["Return"].std() * np.sqrt(252 * multiplier)
    return volatility


def Sharpe(DataFrame, rfr=0.0002):
    """
    Calculate the Sharpe Ratio
    
    Input:
    The price DataFrame with the return column
    rfr - the risk free rate, typically the 3 Month Treasure Bill Rate
    """
    df = DataFrame.copy()
    sr = (CAGR(df) - rfr) / Volatility(df)
    return sr


def MaxDD(DataFrame):
    """
    Calculate the Maximum Drawdown
    
    Input:
    The price DataFrame with the return column
    """
    df = DataFrame.copy()
    df["cumReturn"] = (1 + df["Return"]).cumprod()
    df["cumRollingMax"] = df["cumReturn"].cummax()
    df["Drawdown"] = df["cumRollingMax"] - df["cumReturn"]
    df["DrawdownPct"] = df["Drawdown"] / df["cumRollingMax"]
    return df["DrawdownPct"].max()


def Win_Rate(DataFrame, logReturn=True):
    """
    Calculate the win rate
    
    Input:
    The price DataFrame with the return column
    logReturn - type of the return
    """
    df = DataFrame["Return"]
    if logReturn == True:
        win = df[df > 0]
        lose = df[df < 0]
    else:
        win = df[df > 1]
        lose = df[df < 1]
    return len(win) / (len(win) + len(lose))


def Mean_Return(DataFrame, logReturn=True):
    """
    Calculate the mean return of all trades
    
    Input:
    The price DataFrame with the return column
    logReturn - type of the return
    """
    return_ = DataFrame["Return"]
    if logReturn == True:
        column = return_.dropna()
    else:
        column = (return_ - 1).dropna()
    return column[column != 0].mean()


def Mean_Return_Winning(DataFrame, logReturn=True):
    """
    Calculate the mean return of winning trades
    
    Input:
    The price DataFrame with the return column
    logReturn - type of the return
    """
    return_ = DataFrame["Return"]
    if logReturn == True:
        column = return_.dropna()
    else:
        column = (return_ - 1).dropna()
    return column[column > 0].mean()


def Mean_Return_Losing(DataFrame, logReturn=True):
    """
    Calculate the mean return of losing trades
    
    Input:
    The price DataFrame with the return column
    logReturn - type of the return
    """
    return_ = DataFrame["Return"]
    if logReturn == True:
        column = return_.dropna()
    else:
        column = (return_ - 1).dropna()
    return column[column < 0].mean()


def Max_Consecutive_Loss(DataFrame, logReturn=True):
    """
    Calculate the maximum consecutive loss
    
    Input:
    The price DataFrame with the return column
    logReturn - type of the return
    """
    return_ = DataFrame["Return"]
    column = return_.dropna()
    if logReturn == True:
        category = np.where(column < 0, 1, 0)
    else:
        category = np.where(column < 1, 1, 0)
    consecutive = []
    count = 0
    for i in range(len(category)):
        if category[i] == 0:
            count = 0
        else:
            count += 1
            consecutive.append(count)
    return max(consecutive)
