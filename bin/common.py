import glob
import logging

def read_files_with_prefix(prefix):
    matching_files = glob.glob(prefix+"*")
    logging.info("Found %d matching files for prefix %s" % (len(matching_files), prefix))
    logging.info("files are %s ... %s" % (matching_files[0:5], matching_files[-5:-1]))
    return matching_files
