#                                              My Solve QUBO
########################################################################################################################
# The following is a class which solves QUBO's on the D-Wave. It takes a QUBO dictionary containing the qubit and
# coupler weight assigned to the physical hardware qubits (Q= {(0, 4) = 23.3}). It returns the energy and bit string.
########################################################################################################################

import time
import numpy as np
from dwave.cloud import Client
import dwave
import dwave.embedding
import dimod
from dwave.system.samplers import DWaveSampler



class MySolveQubo:
    def __init__(self, qubo, qubo_dict, user_embedding, runs, spin_reversal, anneal_schedule, chain_strength, j_scale,
                 initial_state, reinitialize):
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # INITIALIZATION:
        # get qubo and qubo_dict from QUBO_linear.py
        self.user_embedding = user_embedding
        self.chain_strength = - chain_strength
        self.j_scale = j_scale
        self.qubo = qubo
        self.qubo_dict = qubo_dict
        self.spin_reversal = spin_reversal
        self.anneal_schedule = anneal_schedule
        self.initial_state = initial_state
        # D-Wave remote connection
        self.url = 'INSERT_URL'
        self.token = 'INSERT_TOKEN'
        # create a remote connection
        self.conn = Client(endpoint=self.url, token=self.token, solver='INSERT_SOVLER_NAME', proxy=None, permissive_ssl=False,
                           request_timeout=60, polling_timeout=None, connection_close=False,
                           headers=None)
        # NB auto_scale is set TRUE so you SHOULD NOT have to rescale the h and J (manual rescaling is optional and
        # included in this program.)
        # "auto_scale": True, "postprocess": "",
        self.params = {"answer_mode": "raw", "auto_scale": True, "postprocess": "", "num_reads": runs,
                       "num_spin_reversal_transforms": self.spin_reversal, "anneal_schedule": self.anneal_schedule,
                       "initial_state": self.initial_state, "reinitialize_state": reinitialize}
        # get the solver
        # get the solver
        self.solver = DWaveSampler(endpoint=self.url, token=self.token, solver='INSERT_SOVLER_NAME')
        self.schedule = None
        self.fidelity = None

        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # EMBEDDING CONTROLS:
        # this logical value indicates whether to clean up the embedding. AKA removing physical variables that are
        # adjacent to a single variable in the same chain or not adjacent to any variables in other chains.
        self.clean = False
        # this logical value indicates whether to smear an embedding to increase the chain size so that the h values do
        # not exceed the scale of J values relative to h_range and J_range respectively.
        self.smear = False
        # a list representing the range of h values, these values are only used when smear = TRUE
        self.h_range = [-2, 2]
        self.J_range = [-1, 1]
        # SOLVE_ISING VARIABLES:
        # the hardware adjacency matrix
        self.Adjacency = None
        # the embedding
        self.Embedding = None

        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # D-WAVE VARIABLES:
        # h is the vector containing the linear ising coefficients
        self.h = None
        self.h_max = None
        # J is the matrix containing the quadratic ising coefficients in dictionary form where each qubit and coupler
        # value is assigned to qubits on the physical hardware
        self.J = None
        self.J1 = None
        # ising_offset is a constant which shifts all ising energies
        self.ising_offset = None
        # embedded h values
        self.h0 = None
        self.h1 = None
        # embedded J values
        self.j0 = None
        # strong output variable couplings
        # self.jc = None
        # what the d-wave returns from solve_ising method
        self.dwave_return = None
        # the unembedded version of what the d-wave returns
        self.unembed = None
        # ising answer
        self.ising_array = None
        num_rows, num_cols = self.qubo.shape
        # The number of qubits
        self.n = num_cols
        self.ising_energy = []
        self.qubo_array = []
        self.qubo_energy = []
        self.h_energy = None
        self.J_energy = None
        self.num_occurrences = None
        self.dwave_solutions = None
        self.raw_array = None
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # QUBO RESULT VARIABLES:
        # qubo answer
        self.qubo_ans = None
        self.qubo_energy = None
        self.dwave_energies = None
        self.timing = None
        self.embedding_time = None
        self.probability_of_success = None
        self.dwave_raw_array = None

    def solvequbo(self):

        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # CONVERSIONS AND RESCALING:
        # convert qubo to ising
        (self.h, self.J, self.ising_offset) = dimod.utilities.qubo_to_ising(self.qubo_dict)
        # Even though auto_scale = TRUE, we are rescaling values
        # Normalize h and J to be between +/- 1
        self.h_max = max(list(map(abs, self.h.values())))

        j_max = max([abs(x) for x in list(self.J.values())])

        # if len(self.J.values()) > 0:
        #     j_max = max([abs(x) for x in self.J.values()])
        # else:
        #     j_max = 1

        # In [0,1], this scales down J values to be less than jc
        # j_scale = 1
        # Use the largest large value
        if self.h_max > j_max:
            j_max = self.h_max
        # This is the actual scaling
        rescale = self.j_scale / j_max
        self.h1 = dict((k, (v * rescale)) for k, v in self.h.items())

        if len(list(self.J.values())) > 0:
            self.J1 = {key: rescale*val for key, val in list(self.J.items())}
        else:
            self.J1 = self.J

        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # EMBEDDING:
        # Embed the rescale values into the hardware graph
        [self.h0, self.j0] = dwave.embedding.embed_ising(self.h1, self.J1, self.Embedding, self.Adjacency,
                                                         chain_strength=self.chain_strength)

        self.dwave_return = self.solver.sample_ising(self.h0, self.j0, **self.params)
        self.dwave_raw_array = self.dwave_return.record.sample
        self.num_occurrences = self.dwave_return.record.num_occurrences
        self.energies = self.dwave_return.record.energy

        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

        bqm = dimod.BinaryQuadraticModel.from_ising(self.h1, self.J1, 0.0)

        unembed = dwave.embedding.unembed_sampleset(self.dwave_return, self.Embedding, bqm, chain_break_fraction=True)
        self.ising_array = unembed.record.sample

        # convert ising string to qubo string
        self.qubo_array = self.ising_array
        self.ising_energy = np.zeros(len(self.ising_array))
        self.qubo_energy = np.zeros(len(self.ising_array))

        # Because the problem is unembedded, the energy will be different for the embedded, and unembedded problem.
        # ising_energies = dwave_return['energies']
        for i in range(len(self.ising_array)):
            unembedded_array = self.ising_array[i]
            self.h_energy = sum(list(self.h1.values())[v] * val for v, val in enumerate(unembedded_array))
            self.J_energy = sum(self.J1[(u, v)] * unembedded_array[u] * unembedded_array[v] for u, v in self.J1)

            self.ising_energy[i] = (self.h_energy + self.J_energy)
            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            # CONVERT ANSWER WITH ENERGY TO QUBO FORM:
            # Rescale and add back in the ising_offset and another constant

            self.qubo_energy[i] = ((self.ising_energy[i] / rescale) + self.ising_offset)

            # QUBO RESULTS:
            self.qubo_array[i] = [int(x + 1) / 2 for x in self.qubo_array[i]]




