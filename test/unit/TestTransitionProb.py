import unittest
import numpy as np

import emission.simulation.transition_prob as estp

class TestTransitionProb(unittest.TestCase):
    def testGetMarkovChainAllEntries(self):
        labels = ["home", "work", "family"]
        prob_matrix = [[0.4, 0.3, 0.3],
                       [0.3, 0.4, 0.3],
                       [0.3, 0.3, 0.4]]
        mc = estp.get_markov_chain(labels, prob_matrix)
        self.assertSetEqual(mc.states(), set(labels))
        self.assertEqual(mc["home", "work"], 0.3)
        self.assertEqual(mc["family", "work"], 0.3)

    def testGetMarkovChainPartialEntries(self):
        labels = ["home", "work", "family"]
        prob_matrix = [[0.4, 0.3, 0],
                       [0.3, 0.4, 0.3],
                       [1, 0, 0]]
        mc = estp.get_markov_chain(labels, prob_matrix)
        self.assertSetEqual(mc.states(), set(labels))
        self.assertEqual(mc["home", "work"], 0.3/0.7)
        self.assertEqual(mc["family", "work"], 0)

    def testGetMarkovChainWeightsNotProb(self):
        labels = ["home", "work", "family"]
        prob_matrix = [[10, 3, 0],
                       [7, 10, 3],
                       [1, 0, 0]]
        mc = estp.get_markov_chain(labels, prob_matrix)
        self.assertSetEqual(mc.states(), set(labels))
        self.assertEqual(mc["home", "work"], 3/13)
        self.assertEqual(mc["work", "work"], 10/20)
        self.assertEqual(mc["family", "work"], 0)
        self.assertEqual(mc["family", "home"], 1)

    def testGenRandomZero(self):
        tp = estp.generate_random_transition_prob(0)
        self.assertEqual(tp, [])

    def testGenRandomNonZero(self):
        tp = estp.generate_random_transition_prob(10)
        # print(tp)
        tparray = np.asarray(tp)
        self.assertEqual(len(tp), 10, "check row count")
        self.assertEqual(len(tp[0]), 10, "checking col count for first row")
        self.assertTrue((tparray.diagonal() == np.zeros(10)).all(), "checking that diagonal is zero")
        self.assertAlmostEqual(sum(tp[0]), 1, msg="check prob sum for first row")
        self.assertAlmostEqual(sum(tp[-1]), 1, msg="check prob sum for last row")

    def testCounter(self):
        import pykov
        mc = pykov.Chain()
        mc["A", "B"] += 1
        self.assertEqual(mc["A", "B"], 1, msg="Increment counter once")
        mc["A", "B"] += 1
        self.assertEqual(mc["A", "B"], 2, msg="Increment counter twice")

    def testGenerateModeProbs(self):
        mode_weight_map = {"WALK": 2, "BICYCLE": 5, "TRANSIT": 2, "CAR": 1}
        mw = estp.generate_mode_probs(mode_weight_map)
        # print(mw)
        self.assertAlmostEqual(mw["CAR"], 1, msg="check sum of mode probabilities")

    def testGenerateModeProbsSubset(self):
        mode_weight_map = {"TRANSIT": 2, "CAR": 1}
        mw = estp.generate_mode_probs(mode_weight_map)
        # print(mw)
        self.assertAlmostEqual(mw["CAR"], 1, msg="check sum of mode probabilities for a subset")

    def testGenerateRandomModeFromCDF(self):
        mode_pdf_dict = {"WALK": 0.2, "BICYCLE": 0.5, "TRANSIT": 0.2, "CAR": 0.1}
        mode_cdf_dict = {"WALK": 0.2, "BICYCLE": 0.7, "TRANSIT": 0.9, "CAR": 1.0}
        # Generate 100,000 random modes, check to see that it is close to the
        # desired distribution
        N_RUNS = 100000
        gen_pdf_dict = {"WALK": 0, "BICYCLE": 0, "TRANSIT": 0, "CAR": 0}
        for _ in range(N_RUNS):
            mw = estp.generate_random_mode_from_cdf(mode_cdf_dict)
            gen_pdf_dict[mw] = gen_pdf_dict[mw] + 1

        print("After generating %d random modes, distribution is %s" % (N_RUNS, gen_pdf_dict))
        for k in mode_cdf_dict.keys():
            self.assertAlmostEqual(gen_pdf_dict[k]/N_RUNS, mode_pdf_dict[k], places=2,
                msg="check final probability distribution for mode %s" % k)
