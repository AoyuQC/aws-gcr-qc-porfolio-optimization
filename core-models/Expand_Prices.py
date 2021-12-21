#                                                    EXPAND RETURNS
########################################################################################################################
#   Create historical price data columns that represent various percentages of the budget for analysis. For example, if
#   the budget is 20 and the price for a whole crypto-coin is 100, one could use analyze various percentages on the
#   coin based on the budget: 5, 10, 15, and 20 to find the best option. This, of course, increases the search space.
########################################################################################################################

import numpy as np


class ExpandPriceData:
    def __init__(self, budget, slices, raw_price_data):
        # ----------------------INITIALIZE------------------------------ #
        # The number of slicess (AKA slices) to analyse including 100%
        self.slices = slices
        self.b = budget

        # num_rows = the amount of historical data collected, num_columns = the number of crypto-currencies

        num_rows, num_cols = raw_price_data.shape

        # ----------------------- slices List --------------------------#
        # The list of slicess of the budget being used to analyze various ranges of the budget for each
        # cryptocurrency.
        self.slices_list = np.zeros(self.slices)
        self.slices_list[0] = 1
        for i in range(1, self.slices):
            self.slices_list[i] = float(1) / float(2 ** i)
        self.slices_list = np.array(self.slices_list)

        self.price_data_expanded = None

        for i in range(num_cols):

            asset_prices = np.zeros((num_rows, self.slices))
            norm_price_factor = budget / raw_price_data[num_rows - 1, i]
            for j in range(self.slices):
                for k in range(num_rows):
                    asset_prices[k, j] = raw_price_data[k, i] * self.slices_list[j] * norm_price_factor
            if i == 0:
                self.price_data_expanded = asset_prices
            else:

                self.price_data_expanded = np.append(self.price_data_expanded, asset_prices, 1)