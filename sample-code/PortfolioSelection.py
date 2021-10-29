#                                        PORTFOLIO SELECTION
########################################################################################################################
#
########################################################################################################################

# Imports the stock file as csv
import numpy as np
from Covariance_calculator import Covariance
from ExpectedReturn_calculator import ExpectedReturns
from Expand_Prices import ExpandPriceData


class PortfolioSelection:

    def __init__(self, theta_one, theta_two, theta_three, price_data, num_slices, covariance):
        # ------  INITIALIZE INPUT DATA ----- #
        # The covariance matrix (if already known)
        self.covariance = covariance
        #  The weight on return term
        self.theta_one = theta_one
        #  The weight on prices AKA the penalty
        self.theta_two = theta_two
        #  The weight on the covariance term AKA portfolio diversity
        self.theta_three = theta_three
        # the budget
        self.b = 1
        # The raw price data
        self.price_data = price_data
        # The number of slices to analyze for each asset. This translates to the granularity in fractions of price.
        self.num_slices = num_slices

        if price_data is not None:
            # ------ EXPAND PRICES  ----- #
            expand = ExpandPriceData(self.b, self.num_slices, self.price_data)
            self.price_data = expand.price_data_expanded

            # ------ PRICE DATA PARAMETERS  ----- #
            # num_rows = the amount of historical data collected, num_columns = the number of crypto-currencies
            self.num_rows, self.num_cols = self.price_data.shape
            # The current prices:
            self.prices = self.price_data[self.num_rows - 1, :].tolist()
            # The number of assets
            self.n = self.num_cols
            # problem size
            self.problem_size = self.n * self.num_slices

            # ----- GET EXPECTED RETURNS ----- #
            # Use the ExpectedReturns class to calculate the expected returns for each asset.
            expected = ExpectedReturns(self.price_data)
            # Implement simple moving average function.
            expected.sma()
            self.expected_returns = expected.exp_returns

            # ----- COVARIANCE BETWEEN ASSETS ----- #
            # The covariance term
            cov = Covariance(self.price_data)
            self.QUBO_covariance = cov.QUBO_covariance
        else:
            self.num_rows, self.num_cols = self.covariance.shape

            self.n = self.num_cols
            self.expected_returns = np.ones(self.n)
            self.expected_returns = self.expected_returns / 6
            self.QUBO_covariance = self.covariance

        # A diagonal matrix with the vector of expected returns
        self.QUBO_returns = np.diag(self.expected_returns)
        # The linear/ diagonal matrix with price penalties.
        self.QUBO_prices_linear = np.diag([x * (2 * self.b) for x in self.prices])
        # The quadratic/ off-diagonal portion of the price penalty term.
        self.QUBO_prices_quadratic = np.outer(self.prices, self.prices)

        # ----- QUBO FORMATION ----- #
        # The linear QUBO term
        self.qi = -(self.theta_one * self.QUBO_returns) - (self.theta_two * self.QUBO_prices_linear)
        # the quadratic QUBO term
        self.qij = (self.theta_two * self.QUBO_prices_quadratic) + (self.theta_three * self.QUBO_covariance)

