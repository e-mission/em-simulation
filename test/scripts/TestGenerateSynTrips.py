import unittest

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

    def testNoServerEnv(self):
        with open("/dev/null", "w") as devnull:
            retcode = sp.call("PYTHONPATH=. python bin/generate_syn_trips.py 2020/05/04 10",
                stderr=devnull, shell=True)
        self.assertEqual(retcode, 1)


    def testNoTransitionProb(self):
        with open("/dev/null", "w") as devnull:
            retcode = sp.call("PYTHONPATH=. OTP_SERVER=http://dummy python bin/generate_syn_trips.py 2020/05/04 10",
                stderr=devnull, shell=True)
        self.assertEqual(retcode, 1)
