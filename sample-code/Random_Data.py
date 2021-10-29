
#                                      GENERATE RANDOM PRICE DATA FOR TESTING PURPOSES
########################################################################################################################
#   Generates random but realistic looking historical price data by adding a percent change to each new data point in
#   the series.
########################################################################################################################

import numpy as np
import random


class RandomPrices:
    def __init__(self, assets, days, budget, problem_number):
        self.price_data = np.zeros((days * problem_number, assets))
        price = random.Random()
        price.seed(budget / 5)
        percent = random.Random()
        percent.seed(.15)
        for i in range(assets):
            starting_price = price.uniform(budget/10, budget)
            for j in range(days * problem_number):
                percent_change = percent.uniform(-.25, .25)
                self.price_data[j, i] = starting_price + starting_price*percent_change



