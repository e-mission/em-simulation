import unittest

import os
import subprocess as sp

# Successes will need to use docker-compose to ensure that there is a server
# and an OTP instance
class TestLoadToRemoteServer(unittest.TestCase):
    def testNoArguments(self):
        print(">>>> expected error ----")
        with open("/dev/null", "w") as devnull:
            retcode = sp.call("PYTHONPATH=. python bin/load_to_remote_server.py",
                shell=True)
        print("<<<< expected error ----")
        self.assertEqual(retcode, 2)

    def testBothInputs(self):
        print(">>>> expected error ----")
        with open("/dev/null", "w") as devnull:
            retcode = sp.call("PYTHONPATH=. python bin/load_to_remote_server.py --input_file=/tmp/shankari.july-22.timeline --input_prefix=/tmp/filled_pop_ http://server:8080",
                shell=True)
        print("<<<< expected error ----")
        self.assertEqual(retcode, 2)

    def testFileInput(self):
        print(">>>> expected error ----")
        with open("/dev/null", "w") as devnull:
            retcode = sp.call("PYTHONPATH=. python bin/load_to_remote_server.py --input_file=/tmp/shankari.july-22.timeline http://server:8080",
                shell=True)
        print("<<<< expected error ----")
        self.assertEqual(retcode, 1)
