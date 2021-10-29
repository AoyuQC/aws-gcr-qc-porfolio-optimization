#                                              EXPECTED RETURN CALCULATOR
########################################################################################################################
# A factory which calculates the expected return (based on Modern Portfolio Theory estimations) from historical price
# data. The methods/functions include the simple moving average (sma()).
########################################################################################################################


import numpy as np


class ExpectedReturns:

    def __init__(self, price_data):
        self.price_data = price_data
        # num_rows = the amount of historical data collected, num_columns = the number of crypto-currencies
        self.num_rows, self.num_cols = price_data.shape
        # Use pandas to create a dataframe of price_data with the cryptocurrencies names as column lables and default
        # indexing.
        self.daily_return = np.zeros((self.num_rows - 1, self.num_cols))
        self.exp_returns = np.zeros(self.num_cols)
        self.av_monthly = None
        self.av_yearly = None
        self.prices = None
        self.prices = None
        self.price_table = None

    #  A SIMPLE MOVING AVERAGE takes the daily average returns and the average which can be applied over any period
    #  of time. The data is also trimmed using a winsorizing method. This is best applied to longer term investments. If
    #  a shorter-term simple moving average is above a longer-term average, an uptrend is expected. On the other hand, a
    #  long-term average above a shorter-term average signals a downward movement in the trend.
    def sma(self):
        # Calculate daily_return array which contains the daily returns contained in the historical price_data array:
        for i in range(self.num_cols):
            for j in range(self.num_rows - 1):
                self.daily_return[j, i] = self.price_data[j + 1, i] - self.price_data[j, i]
            self.exp_returns[i] = np.mean(self.daily_return[:, i])



