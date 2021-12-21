########################################################################################################################
#   The following class is the formulation of QUBO from the the weights (theta_one, theta_two, and theta_three),
#   the budget (b), the historical price data for each asset as a 2D array (price_data), and the expected returns of
#   each asset as a 1D array. It contains two functions: qubo_direct() which solves the QUBO directly with brute force
#   and qubo_dwave() which send the QUBO as a dictionary to the D-Wave to be solved using the MySolveQubo class and
#   prepares the solution.
########################################################################################################################
from SymmetricToTriangular import TriangleGenerator


class QUBO:

    def __init__(self, qi, qij):
        # ------  INITIALIZE INPUT DATA ----- #
        # Linear QUBO term
        self.qi = qi
        # Quadratic QUBO term
        self.qij = qij
        self.num_rows, self.num_cols = self.qij.shape
        self.n = self.num_cols

        # ------  BUILD QUBO ----- #
        self.qubo = qi + qij
        # Make QUBO either upper or lower triangular using the upper() and lower() functions from the TriangleGenerator
        # class with upper_matrix and lower_matrix variables respectfully.
        self.triangle = TriangleGenerator(self.n, self.qubo)
        self.triangle.upper()
        self.qubo = self.triangle.upper_matrix
        # The QUBO matrix in dictionary form where each qubit(diagonal) and coupling(off-diagonal) weight is assigned to
        # physical qubits on the hardware (minor embedding).
        self.qubo_dict = {}
        self.qubo_dict.update({(i, j): self.qubo[i][j] for i in range(self.n) for j in range(self.n)})





