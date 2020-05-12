import unittest

import os
import subprocess as sp

# Successes will need to use docker-compose to ensure that there is a server
# and an OTP instance
class TestGenerateSynTripFailures(unittest.TestCase):
    def testNoArguments(self):
        print(">>>> expected error ----")
        with open("/dev/null", "w") as devnull:
            retcode = sp.call("PYTHONPATH=. python bin/fill_trajectories.py",
                shell=True)
        print("<<<< expected error ----")
        self.assertEqual(retcode, 2)

    def testNoOtpServer(self):
        print(">>>> expected error ----")
        with open("/dev/null", "w") as devnull:
            retcode = sp.call("PYTHONPATH=. python bin/fill_trajectories.py 2020/05/04",
                shell=True)
        print("<<<< expected error ----")
        self.assertEqual(retcode, 1)

    def testNoInputFile(self):
        print(">>>> expected error ----")
        with open("/dev/null", "w") as devnull:
            retcode = sp.call("PYTHONPATH=. OTP_SERVER=http://otp python bin/fill_trajectories.py 2020/05/04",
                shell=True)
        print("<<<< expected error ----")
        self.assertEqual(retcode, 1)
