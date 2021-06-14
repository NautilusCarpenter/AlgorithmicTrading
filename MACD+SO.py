from base import Base_App
from command import (
    generateOrderId,
    placeOrder,
    cancelOrder,
    showOpenOrder,
    showPosition,
    showAccountSummary,
    showPnL,
)
from contract import Historical_Data, toDataFrame, US_Stock
from indicator import MACD, SO, ATR
from metric import Daily_Return, CAGR, Volatility, Sharpe, MaxDD
from order import Limit_Order, Market_Order, Stop_Order
import pandas as pd
import threading
import time


# ########## BLOCK START - Strategy ########## #
class Strategy(Base_App):
    pass


# ########## BLOCK END - Strategy ########## #


# ########## BLOCK START - Connect ########## #
def WebSocket_Connection(app):
    app.run()


strategy = Strategy()
strategy.connect("127.0.0.1", 7497, clientId=1)
time.sleep(1)

connection = threading.Thread(target=WebSocket_Connection, args=[strategy], daemon=True)
connection.start()
time.sleep(1)
print("Connection status:", strategy.isConnected())
# ########## BLOCK END - Connect ########## #


# ########## BLOCK START - Backtest ########## #
def backtest(universe, duration, barSize):
    """
    MACD + Stochastic Oscillator strategy (long only)

    BUY signal:
    1. MACD greater than MACD signal
    2. SO greater than 30
    3. SO increasing

    Trailing stop loss:
    If not triggered, stop loss to be revised after each period as [close - 60 period ATR]
    """
    # Show current time on server
    strategy.reqCurrentTime()
    df = toDataFrame(strategy, universe, duration, barSize)
    print(df)
    signal_ = {}
    return_ = {}
    count_ = {}
    for symbol in universe:
        print("Calculating MACD+SO for:", symbol)
        df[symbol]["MACD"] = MACD(df[symbol])["MACD"]
        df[symbol]["MACD_signal"] = MACD(df[symbol])["MACD_signal"]
        df[symbol]["SO"] = SO(df[symbol])
        df[symbol]["ATR"] = ATR(df[symbol], 60)
        df[symbol].dropna(inplace=True)
        signal_[symbol] = ""
        return_[symbol] = [0]
        count_[symbol] = 0
    for symbol in universe:
        print("Calculating daily returns for:", symbol)
        for i in range(1, len(df[symbol])):
            if signal_[symbol] == "":
                return_[symbol].append(0)
                crit1 = df[symbol]["MACD"][i] > df[symbol]["MACD_signal"][i]
                crit2 = df[symbol]["SO"][i] > 30
                crit3 = df[symbol]["SO"][i] > df[symbol]["SO"][i - 1]
                if crit1 and crit2 and crit3:
                    signal_[symbol] = "BUY"
                    count_[symbol] += 1
            elif signal_[symbol] == "BUY":
                crit4 = (
                    df[symbol]["Low"][i]
                    < df[symbol]["Close"][i - 1] - df[symbol]["ATR"][i - 1]
                )
                if crit4:
                    signal_[symbol] = ""
                    count_[symbol] += 1
                    return_[symbol].append(
                        (
                            (df[symbol]["Close"][i - 1] - df[symbol]["ATR"][i - 1])
                            / df[symbol]["Close"][i - 1]
                        )
                        - 1
                    )
                else:
                    return_[symbol].append(
                        (df[symbol]["Close"][i] / df[symbol]["Close"][i - 1]) - 1
                    )
        df[symbol]["Return"] = return_[symbol]
    return df


# # ########## BLOCK END - Backtest ########## #


# # ########## BLOCK START - Trade ########## #
def trade(universe, duration, barSize, capital):
    strategy.reqPositions()
    time.sleep(2)
    position_df = strategy.position_df
    position_df.drop_duplicates(inplace=True, ignore_index=True)
    strategy.reqOpenOrders()
    time.sleep(2)
    order_df = strategy.order_df
    for idx, symbol in enumerate(universe):
        print("Starting to process the data for:", symbol)
        Historical_Data(strategy, idx, US_Stock(symbol), duration, barSize)
        time.sleep(3)
        df = pd.DataFrame(strategy.historical_data[idx])
        df.set_index("Date", inplace=True)
        df["MACD"] = MACD(df)["MACD"]
        df["MACD_signal"] = MACD(df)["MACD_signal"]
        df["SO"] = SO(df)
        df["ATR"] = ATR(df, 60)
        df.dropna(inplace=True)
        quantity = int(capital / df["Close"][-1])
        # Skip the stocks that are too expensive
        if quantity == 0:
            continue
        signal_crit = (
            df["MACD"][-1] > df["MACD_signal"][-1]
            and df["SO"][-1] > 30
            and df["SO"][-1] > df["SO"][-2]
        )
        if (len(position_df) == 0) or (
            len(position_df) != 0 and symbol not in position_df["Symbol"].tolist()
        ):
            if signal_crit:
                orderId = generateOrderId(strategy)
                placeOrder(
                    strategy, orderId, US_Stock(symbol), Market_Order("BUY", quantity)
                )
                orderId = generateOrderId(strategy)
                placeOrder(
                    strategy,
                    orderId,
                    US_Stock(symbol),
                    Stop_Order(
                        "SELL", quantity, round(df["Close"][-1] - df["ATR"][-1], 1),
                    ),
                )
        elif len(position_df) != 0 and symbol in position_df["Symbol"].tolist():
            position_crit = (
                position_df[position_df["Symbol"] == symbol]["Position"]
                .sort_values(ascending=True)
                .values[-1]
            )
            if position_crit == 0:
                if signal_crit:
                    orderId = generateOrderId(strategy)
                    placeOrder(
                        strategy,
                        orderId,
                        US_Stock(symbol),
                        Market_Order("BUY", quantity),
                    )
                    orderId = generateOrderId(strategy)
                    placeOrder(
                        strategy,
                        orderId,
                        US_Stock(symbol),
                        Stop_Order(
                            "SELL", quantity, round(df["Close"][-1] - df["ATR"][-1], 1),
                        ),
                    )
            elif position_crit > 0:
                pre_orderId = (
                    order_df[order_df["Symbol"] == symbol]["OrderId"]
                    .sort_values(ascending=True)
                    .values[-1]
                )
                pre_quantity = (
                    position_df[position_df["Symbol"] == symbol]["Position"]
                    .sort_values(ascending=True)
                    .values[-1]
                )
                cancelOrder(strategy, pre_orderId)
                orderId = generateOrderId(strategy)
                placeOrder(
                    strategy,
                    orderId,
                    US_Stock(symbol),
                    Stop_Order(
                        "SELL", pre_quantity, round(df["Close"][-1] - df["ATR"][-1], 1),
                    ),
                )


# ########## BLOCK END - Trade ########## #


# ########## BLOCK START - Run ########## #
if __name__ == "__main__":
    """
    SECTION: Define the parameters
    """
    universe = [
        "FB",
        "AMZN",
        "INTC",
        # "MSFT",
        # "AAPL",
        # "GOOG",
        # "CSCO",
        # "CMCSA",
        # "ADBE",
        # "NVDA",
        # "NFLX",
        # "PYPL",
        # "AMGN",
        # "AVGO",
        # "TXN",
        # "CHTR",
        # "QCOM",
        # "GILD",
        # "FISV",
        # "BKNG",
        # "INTU",
        # "ADP",
        # "CME",
        # "TMUS",
        # "MU",
    ]
    duration = "5 D"
    barSize = "5 mins"
    capital = 1000
    """
    SECTION: Run backtest
    """
    bt = backtest(universe, duration, barSize)
    btCAGR = CAGR(bt[universe[1]], False, barSize)
    print(btCAGR)
    # btReturn = Daily_Return(bt[universe[0]])
    # print(btReturn)
    # btVolatility = Volatility(btReturn)
    # print(btVolatility)
    # btSharpe = Sharpe(btReturn)
    # print(btSharpe)
    # btMaxDD = MaxDD(btReturn)
    # print(btMaxDD)
    """
    SECTION: Paper trading
    """
    # starttime = time.time()
    # timeout = time.time() + 60 * 10
    # while time.time() <= timeout:
    #     trade(universe, duration, barSize, capital)
    #     time.sleep(300 - ((time.time() - starttime) % 300.0))
    """
    SECTION: Cancel all open orders and Close all postions 
    """
    # strategy.reqGlobalCancel()
    # orderId = generateOrderId(strategy)
    # strategy.reqPositions()
    # time.sleep(2)
    # position = strategy.position_df
    # position.drop_duplicates(inplace=True, ignore_index=True)
    # for symbol in position["Symbol"]:
    #     quantity = position[position["Symbol"] == symbol]["Position"].values[0]
    #     strategy.placeOrder(orderId, US_Stock(symbol), Market_Order("SELL", quantity))
    #     orderId += 1
    """
    SECTION: Testing
    """
# ########## BLOCK END - Run ########## #


# ########## BLOCK START - Disconnect ########## #
strategy.disconnect()
# ########## BLOCK END - Disconnect ########## #
