#                                                    COVARIANCE CALCULATOR
########################################################################################################################
#   Calculate the covariance between assets matrix using historical price data. The covariance matrix is used to
#   implement the term for diversity in the portfolio selection problem.
########################################################################################################################

import numpy as np


class Covariance:
    def __init__(self, price_data):
        # num_rows = the amount of historical data collected, num_columns = the number of crypto-currencies
        num_rows, num_cols = price_data.shape
        self.QUBO_covariance = np.zeros((num_cols, num_cols))
        # Multiply each element by the covariance for ith and jth stock's return data. np.cov gives the covariance
        # matrix with off-diagonal([0][1] and [1][0]) elements being the covariance value.
        for i in range(num_cols):
            for j in range(num_cols):
                self.QUBO_covariance[i, j] = ((price_data[num_rows - 1, i] - np.mean(price_data[:, i])) * (price_data[num_rows - 1, j] - np.mean(price_data[:, j]))) / (num_cols - 1)
                # self.QUBO_covariance[i, j] = np.cov(price_data[:, i], price_data[:, j])[0][1]
