from ibapi.contract import Contract
import pandas as pd
import time


def Historical_Data(app, reqId, contract, duration, barSize):
    app.reqHistoricalData(
        reqId=reqId,
        contract=contract,
        endDateTime="",
        durationStr=duration,
        barSizeSetting=barSize,
        whatToShow="ADJUSTED_LAST",
        useRTH=1,
        formatDate=1,
        keepUpToDate=False,
        chartOptions=[],
    )


def US_Stock(symbol, secType="STK", currency="USD", exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = secType
    contract.currency = currency
    contract.exchange = exchange
    return contract


def toDataFrame(app, universe, duration, barSize):
    historical_dict = {}
    for idx, symbol in enumerate(universe):
        try:
            Historical_Data(app, idx, US_Stock(symbol), duration, barSize)
            time.sleep(3)
            historical_dict[symbol] = pd.DataFrame(app.historical_data[idx])
            historical_dict[symbol].set_index("Date", inplace=True)
            print("Finished extracting data for {}: CONTINUED.".format(symbol))
        except:
            print(
                "Error encountered when extracting data for {}: SKIPPED.".format(symbol)
            )
    return historical_dict
