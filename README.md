# Algorithmic Trading with Interactive Brokers API
Inspired by Mayank Rasu (https://rasuquant.com/)

**Frameworks**:

* base.py - the base class of the trading app, containing EClient and EWrapper functions from Interactive Brokers API
* command.py - functions to call the EWrapper functions
* contract.py - functions to orgnise and clean the historical data of certain types of securities
* indicator.py - functions to calculate normal techincal indicators
* metric.py - functions to calculate various metrics that measure the performance of strategies
* order.py - contains functions to call various types of orders


**Strategies**:

* MACD+SO.py - the strategy of Moving Average Convergence Divergence + Stochastic Oscillator, including the functions to back-test and paper-trade
* ORB.py - the strategy of Opening Range Breakout (https://www.warriortrading.com/opening-range-breakout/)