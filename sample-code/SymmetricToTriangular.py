#                                              Symmetric Matrix to Triangular Matrix
########################################################################################################################
#   The following is to generate triangular matrices (which is easier for the D-Wave to embed) from symmetric QUBO
#   matrices. You can choose upper or lower triangular matrices by choosing the upper or lower function.
########################################################################################################################


class TriangleGenerator:
    def __init__(self, n, q):
        self.n = n
        self.q = q
        self.i = None
        self.upper_matrix = None
        self.lower_matrix = None

    def upper(self):
        for col in range(0, self.n-1):
            for row in range(col+1, self.n):
                self.q[row, col] = 0
        for row in range(0, self.n-1):
            for col in range(row+1, self.n):
                self.q[row, col] = 2 * self.q[row, col]
        self.upper_matrix = self.q

    def lower(self):
        for row in range(0, self.n-1):
            for col in range(row+1, self.n):
                self.q[row, col] = 0
        for col in range(0, self.n-1):
            for row in range(col+1, self.n):
                self.q[row, col] = 2 * self.q[row, col]
        self.lower_matrix = self.q

