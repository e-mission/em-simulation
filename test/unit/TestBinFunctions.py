import unittest
import tempfile
import re

import common
import load_to_remote_server as ltrs

class TestTransitionProb(unittest.TestCase):
    def testReadFilesWithPrefix(self):
        testPrefix="test_read_files_with_prefix_"
        with tempfile.TemporaryDirectory() as tmpdirname:
            for i in range(10):
                with open(tmpdirname+"/"+testPrefix+str(i)+".timeline", "w") as fp:
                    fp.write("Added file %d" % i)
            matching_files = common.read_files_with_prefix(tmpdirname+"/"+testPrefix)
            self.assertEqual(len(matching_files), 10)
            self.assertIn(tmpdirname+"/"+testPrefix+"0.timeline", matching_files)
            self.assertIn(tmpdirname+"/"+testPrefix+"9.timeline", matching_files)

    def testGetEmail(self):
        test_prefix = "/tmp/filled_pop_"
        regex = re.compile(r"{prefix}(\S*).timeline".format(prefix=test_prefix))

        # works with _
        self.assertEqual(ltrs.get_email("/tmp/filled_pop_Tour_0.timeline", regex),
            "Tour_0")

        # works with -
        self.assertEqual(ltrs.get_email("/tmp/filled_pop_Tour-0.timeline", regex),
            "Tour-0")

        # works with .
        self.assertEqual(ltrs.get_email("/tmp/filled_pop_Tour.0.timeline", regex),
            "Tour.0")

        # fails with ' '
        self.assertIsNone(ltrs.get_email("/tmp/filled_pop_Tour 0.timeline", regex))

        # fails if there is no timeline
        self.assertIsNone(ltrs.get_email("/tmp/filled_pop_Tour_0", regex))
