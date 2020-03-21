import unittest

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
        self.assertEqual(len(tp), 10, "check row count")
        self.assertEqual(len(tp[0]), 10, "checking col count for first row")
        self.assertAlmostEqual(sum(tp[0]), 1, msg="check prob sum for first row")
        self.assertAlmostEqual(sum(tp[-1]), 1, msg="check prob sum for last row")
