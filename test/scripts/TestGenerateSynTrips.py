import unittest
import tempfile

import os
import subprocess as sp

# Successes will need to use docker-compose to ensure that there is a server
# and an OTP instance
class TestGenerateSynTripFailures(unittest.TestCase):
    def testNoArguments(self):
        with open("/dev/null", "w") as devnull:
            retcode = sp.call("PYTHONPATH=. python bin/generate_syn_trips.py",
                stderr=devnull, shell=True)
        self.assertEqual(retcode, 2)

    def testNoTransitionProb(self):
        with open("/dev/null", "w") as devnull:
            retcode = sp.call("PYTHONPATH=. OTP_SERVER=http://dummy python bin/generate_syn_trips.py 10",
                stderr=devnull, shell=True)
        self.assertEqual(retcode, 1)

    def testWorkingVersion(self):
        with tempfile.TemporaryDirectory() as td:
            outfile = td +"/population.xml"
            retcode = sp.call("PYTHONPATH=. python bin/generate_syn_trips.py 10 --generate_random_prob --outfile %s" % outfile, shell=True)
            self.assertEqual(retcode, 0)
            self.assertTrue(os.path.exists(outfile))
