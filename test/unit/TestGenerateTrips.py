import unittest
import json
import haversine as hv
import math
import numpy as np

import emission.simulation.generate_trips as esgt
import emission.simulation.transition_prob as estp

class TestGenerateTrips(unittest.TestCase):
    def setUp(self):
        with open("conf/tour.conf.sample") as tcs:
            self.sampleTourConfig = json.load(tcs)
        n_labels = len(self.sampleTourConfig["locations"])
        self.sampleTourConfig["transition_probs"] = estp.generate_random_transition_prob(n_labels)

    def testInitDataFrame(self):
        labels = ["foo", "bar", "baz"]
        df = esgt._init_dataframe(labels, dtype=dict)
        self.assertEqual(len(df["foo"]), 3, "test init row length")
        self.assertIsNone(df.loc["foo", "bar"], "test init cell values")
        return df

    def testModifyDataFrame(self):
        df = self.testInitDataFrame()

        foobar = {"BICYCLE": 0.5}
        df.at["foo", "bar"] = foobar
        self.assertEqual(df.loc["foo", "bar"]["BICYCLE"], 0.5, "test modify cell")

        foobaz = {"TRANSIT": 0.5, "CAR": 0.5}
        df.at["foo", "baz"] = foobaz
        self.assertEqual(df.loc["foo", "baz"]["CAR"], 0.5, "test modify cell with two entries")

        self.assertEqual(df.loc["foo"].to_list(), [None, foobar, foobaz], "test access modified row")

    def testHaversineLibrary(self):
        # verified by using https://www.doogal.co.uk/MeasureDistances.php
        self.assertAlmostEqual(hv.haversine(
            [37.77264255,-122.399714854263],
            [37.42870635,-122.140926605802]),
            44.52, places=2, msg="Palo Alto to SF is 44 km as the crow files")

        self.assertAlmostEqual(hv.haversine(
            [37.77264255,-122.399714854263],
            [37.87119, -122.27388]),
            15.56, places=2, msg="SF to Berkeley is 15 km as the crow files")

    def testCreateDistMatrix(self):
        dist_df = esgt.create_dist_matrix(self.sampleTourConfig)
        self.assertEqual(dist_df.loc["home", "home"], 0, msg="same location = 0 km")
        self.assertAlmostEqual(dist_df.loc["home", "work"], 44.52, places=2,
            msg="home to work = SF to Palo Alto = 44 km")
        self.assertAlmostEqual(dist_df.loc["work", "home"], 44.52, places=2,
            msg="home to work = Palo Alto to SF = 44 km")
        self.assertAlmostEqual(dist_df.loc["home", "family"], 15.56, places=2,
            msg="home to family = SF to Berkeley = 15 km")
        self.dist_df = dist_df

    def testCalculatePossibleModes(self):
        self.testCreateDistMatrix()
        possible_mode_df = esgt.calculate_possible_modes(self.sampleTourConfig, self.dist_df)
        self.assertIsNone(possible_mode_df.loc["home", "home"], "No mode for staying in place")
        self.assertEqual(list(possible_mode_df.loc["home", "work"].keys()), ["TRANSIT", "CAR"], "Too far, can only take motorized")
        self.assertEqual(list(possible_mode_df.loc["work", "home"].values()), [2, 1], "Too far, can only take motorized")
        self.possible_mode_matrix = possible_mode_df

    def testCalculateModeProb(self):
        self.testCalculatePossibleModes()
        mode_prob_matrix = esgt.calculate_mode_prob(self.possible_mode_matrix)
        self.assertAlmostEqual(list(mode_prob_matrix.loc["work", "home"].values())[-1], 1,
            msg="Final entry in CDF should be one")

    def testFreezeDistributions(self):
        dwell_time_frozen = esgt.freeze_dwell_hours_random_generators(self.sampleTourConfig)
        self.assertEqual(dwell_time_frozen["work"].mean(), 8)
        self.assertEqual(dwell_time_frozen["home"].std(), 2)
        self.assertEqual(dwell_time_frozen["family"].support(), (-math.inf, math.inf))

        mode_speed_frozen = esgt.freeze_mode_kmph_random_generators(self.sampleTourConfig)
        self.assertEqual(mode_speed_frozen["WALK"].mean(), 5)
        self.assertEqual(mode_speed_frozen["BICYCLE"].std(), 5)
        self.assertEqual(mode_speed_frozen["TRANSIT"].support(), (-math.inf, math.inf))

    def testFirstDwell(self):
        sample_user = esgt.FakeUser(5, self.sampleTourConfig)
        sample_user.first_dwell()
        # This is a randomly generated value, so we can't really verify what is
        # it supposed to be. The support is (-inf, inf) so it could really be
        # anything. We could check for 2 standard deviations, and comment out
        # if it fails too much. Or just run to ensure that the elapsed time is updated
        self.assertGreater(sample_user._elapsed_mins, 0,
            msg="Elapsed time has not been updated")

        self.assertGreater(sample_user._elapsed_mins, 60,
            msg="Elapsed time is an order of magnitude lower, check scale")

        self.assertLess(sample_user._elapsed_mins, 60 * 60,
            msg="Elapsed time is an order of magnitude lower, check scale")

    def testFirstDwellRV(self):
        sample_user = esgt.FakeUser(5, self.sampleTourConfig)
        first_dwell_rv = sample_user._freeze_first_dwell()
        # print(first_dwell_rv.mean())
        dwell_times = first_dwell_rv.rvs(size=100000)
        # print(dwell_times)
        self.assertAlmostEqual(dwell_times.mean(), 8, places=1,
            msg="check mean of final probability distribution for initial home state")

        self.assertAlmostEqual(dwell_times.std(), 1, places=1,
            msg="check std of final probability distribution for initial home state")

    def testLastDwell(self):
        sample_user = esgt.FakeUser(5, self.sampleTourConfig)
        act = sample_user.last_dwell()
        self.assertIn("@type", act)
        self.assertNotIn("@elapsed_ts", act)
        self.assertNotIn("leg", act)

    def testTakeTrip(self):
        sample_user = esgt.FakeUser(5, self.sampleTourConfig)
        sample_user.first_dwell()
        act = sample_user.take_trip()
        nRetries = 0
        MAX_RETRIES = 10
        while act is None and nRetries < MAX_RETRIES:
            act = sample_user.take_trip()
        # print(act)
        # Again, because this is randomly generated, we cannot check the
        # values, only that they exist and are formatted correctly
        self.assertEqual(act["@type"], "home")
        self.assertIn("leg", act)
        self.assertIn("@mode", act["leg"])
        self.assertIn(act["leg"]["@mode"], ["TRANSIT", "CAR"])

    def testTakeTrips(self):
        sample_user = esgt.FakeUser(5, self.sampleTourConfig)
        act_list = sample_user.take_trips()
        # print(act_list)
        act_pairs = list(zip(act_list[:-1], act_list[1:-1]))
        elapsed_time_diffs = np.asarray([ea["@elapsed_ts"] - sa["@elapsed_ts"] for (sa, ea) in act_pairs])
        # print(elapsed_time_diffs)
        self.assertTrue((elapsed_time_diffs > 0).all(),
            "time is monotonically increasing")
        adjacent_labels = [(ea["@type"], sa["@type"]) for (sa, ea) in act_pairs]
        self.assertEqual(len(adjacent_labels), 4, "Checking number of label pairs")
        duplicate_adjacent_labels = [sl == el for (sl, el) in adjacent_labels]
        # print(duplicate_adjacent_labels)
        self.assertFalse(np.array(duplicate_adjacent_labels).any(), "Checking no duplicate labels")
