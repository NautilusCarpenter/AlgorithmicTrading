import time


def generateOrderId(app):
    app.reqIds(-1)
    time.sleep(1)
    nextOrderId = app.nextValidOrderId
    return nextOrderId


def placeOrder(app, orderId, contract, order):
    app.placeOrder(orderId, contract, order)


def cancelOrder(app, orderId):
    app.cancelOrder(orderId)


def showOpenOrder(app):
    app.reqOpenOrders()
    time.sleep(1)
    order = app.order_df
    return order


def showPosition(app):
    app.reqPositions()
    time.sleep(1)
    position = app.position_df
    return position


def showAccountSummary(app):
    app.reqAccountSummary(1, "All", "$LEDGER:ALL")
    time.sleep(1)
    account = app.account_df
    return account


def showPnL(app):
    app.reqPnL(2, "DU3207075", "")
    time.sleep(1)
    PnL = app.PnL_df
    return PnL
