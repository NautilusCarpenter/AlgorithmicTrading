from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import datetime as dt
import pandas as pd


class IB_Wrapper(EWrapper):
    pass


class IB_Client(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class Base_App(IB_Wrapper, IB_Client):
    def __init__(self):
        IB_Wrapper.__init__(self)
        IB_Client.__init__(self, wrapper=self)
        self.historical_data = {}
        self.account_df = pd.DataFrame(
            columns=["ReqId", "Account", "Tag", "Value", "Currency"]
        )
        self.execution_df = pd.DataFrame(
            columns=[
                "ReqId",
                "PermId",
                "Symbol",
                "SecType",
                "Currency",
                "ExecId",
                "Time",
                "Account",
                "Exchange",
                "Side",
                "Shares",
                "Price",
                "AvPrice",
                "cumQty",
                "OrderRef",
            ]
        )
        self.order_df = pd.DataFrame(
            columns=[
                "PermId",
                "ClientId",
                "OrderId",
                "Account",
                "Symbol",
                "SecType",
                "Exchange",
                "Action",
                "OrderType",
                "TotalQty",
                "CashQty",
                "LmtPrice",
                "AuxPrice",
                "Status",
            ]
        )
        self.pnl_df = pd.DataFrame(
            columns=["ReqId", "DailyPnL", "UnrealizedPnL", "RealizedPnL"]
        )
        self.position_df = pd.DataFrame(
            columns=["Account", "Symbol", "SecType", "Currency", "Position", "Avg cost"]
        )
        self.requestId = 0

    # ########## Inherited methods ########## #
    def accountSummary(self, reqId, account, tag, value, currency):
        super().accountSummary(reqId, account, tag, value, currency)
        account_dict = {
            "ReqId": reqId,
            "Account": account,
            "Tag": tag,
            "Value": value,
            "Currency": currency,
        }
        self.account_df = self.account_df.append(account_dict, ignore_index=True)

    def accountSummaryEnd(self, reqId: int):
        super().accountSummaryEnd(reqId)
        print("AccountSummaryEnd. ReqId:", reqId)

    def contractDetails(self, reqId, contractDetails):
        super().contractDetails(reqId, contractDetails)
        print("ReqId: {}, contract: {}".format(reqId, contractDetails))

    def contractDetailsEnd(self, reqId):
        super().contractDetailsEnd(reqId)
        print("ContractDetailsEnd. ReqId:", reqId)

    def currentTime(self, time):
        print("Current time on server:", dt.datetime.fromtimestamp(time))

    def error(self, reqId, errorCode, errorString):
        super().error(reqId, errorCode, errorString)
        print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)
        print(
            "ExecDetails. ReqId:",
            reqId,
            "Symbol:",
            contract.symbol,
            "SecType:",
            contract.secType,
            "Currency:",
            contract.currency,
            execution,
        )

    def historicalData(self, reqId, bar):
        historical_dict = {
            "Date": bar.date,
            "Open": bar.open,
            "High": bar.high,
            "Low": bar.low,
            "Close": bar.close,
            "Volume": bar.volume,
        }
        if reqId not in self.historical_data:
            self.historical_data[reqId] = [historical_dict]
        else:
            self.historical_data[reqId].append(historical_dict)
        print(
            "HistoricalData. ReqId:",
            reqId,
            "Date:",
            bar.date,
            "Close:",
            bar.close,
            "Volume:",
            bar.volume,
        )

    def historicalDataEnd(self, reqId, start, end):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

    def historicalDataUpdate(self, reqId, bar):
        print("HistoricalDataUpdate. ReqId:", reqId, "BarData.", bar)

    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        order_dict = {
            "PermId": order.permId,
            "ClientId": order.clientId,
            "OrderId": orderId,
            "Account": order.account,
            "Symbol": contract.symbol,
            "SecType": contract.secType,
            "Exchange": contract.exchange,
            "Action": order.action,
            "OrderType": order.orderType,
            "TotalQty": order.totalQuantity,
            "CashQty": order.cashQty,
            "LmtPrice": order.lmtPrice,
            "AuxPrice": order.auxPrice,
            "Status": orderState.status,
        }
        self.order_df = self.order_df.append(order_dict, ignore_index=True)

    def openOrderEnd(self):
        super().openOrderEnd()
        print("OpenOrderEnd")

    def orderStatus(
        self,
        orderId,
        status,
        filled,
        remaining,
        avgFillPrice,
        permId,
        parentId,
        lastFillPrice,
        clientId,
        whyHeld,
        mktCapPrice,
    ):
        super().orderStatus(
            orderId,
            status,
            filled,
            remaining,
            avgFillPrice,
            permId,
            parentId,
            lastFillPrice,
            clientId,
            whyHeld,
            mktCapPrice,
        )
        print(
            "OrderStatus. Id:",
            orderId,
            "Status:",
            status,
            "Filled:",
            filled,
            "Remaining:",
            remaining,
            "AvgFillPrice:",
            avgFillPrice,
            "PermId:",
            permId,
            "ParentId:",
            parentId,
            "LastFillPrice:",
            lastFillPrice,
            "ClientId:",
            clientId,
            "WhyHeld:",
            whyHeld,
            "MktCapPrice:",
            mktCapPrice,
        )

    def pnl(self, reqId, dailyPnL, unrealizedPnL, realizedPnL):
        super().pnl(reqId, dailyPnL, unrealizedPnL, realizedPnL)
        pnl_dict = {
            "ReqId": reqId,
            "DailyPnL": dailyPnL,
            "UnrealizedPnL": unrealizedPnL,
            "RealizedPnL": realizedPnL,
        }
        self.pnl_df = self.pnl_df.append(pnl_dict, ignore_index=True)

    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)
        position_dict = {
            "Account": account,
            "Symbol": contract.symbol,
            "SecType": contract.secType,
            "Currency": contract.currency,
            "Position": position,
            "Avg cost": avgCost,
        }
        self.position_df = self.position_df.append(position_dict, ignore_index=True)

    def positionEnd(self):
        super().positionEnd()
        print("PositionEnd")

    # ########## Self-defined methods ########## #
    def getReqId(self):
        """
        Increment the request_Id with 1 every time the function is called
        """
        self.requestId += 1
        print("ReqId:", self.requestId)
        return self.requestId
