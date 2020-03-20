import unittest

import os
import subprocess as sp

class TestGenerateSynTrips(unittest.TestCase):
    def testNoArguments(self):
        with open("/dev/null", "w") as devnull:
            retcode = sp.call("PYTHONPATH=. python bin/generate_syn_trips.py",
                stderr=devnull, shell=True)
        self.assertEqual(retcode, 2)
            
