from ibapi.order import Order


def Market_Order(action, quantity):
    order = Order()
    order.action = action
    order.orderType = "MKT"
    order.totalQuantity = quantity
    return order


def Limit_Order(action, quantity, lmtPrice):
    order = Order()
    order.action = action
    order.orderType = "LMT"
    order.totalQuantity = quantity
    order.lmtPrice = lmtPrice
    return order


def Stop_Order(action, quantity, stopPrice):
    order = Order()
    order.action = action
    order.orderType = "STP"
    order.totalQuantity = quantity
    order.auxPrice = stopPrice
    return order


def Trailing_Stop_Order(action, quantity, stopPrice, trailingStep=1):
    order = Order()
    order.action = action
    order.orderType = "TRAIL"
    order.totalQuantity = quantity
    order.auxPrice = trailingStep
    order.trailStopPrice = stopPrice
    return order
