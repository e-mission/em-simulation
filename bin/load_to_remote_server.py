import logging

import json
import argparse

import common
import os

import gzip
import requests
import numpy as np
import re

import emission.simulation.fake_user as esfu
import emission.simulation.client as escg

def get_email(filename, regex):
    result = regex.match(filename)
    if result is None:
        return None
    else:
        return result.group(1)

def load_user(client, file_name, email_regex):
    user_email = get_email(file_name, email_regex)
    fake_user_uuid = client.register_fake_user(user_email)
    with open(file_name) as fp:
        entries = json.load(fp)

    print("For user %s, about to push %d entries to server %s" %
        (user_email, len(entries), client_config["emission_server_base_url"]))

    client.sync_data_to_server(user_email, entries,
        lambda r: print("Success loading data %d" % r.status_code),
        lambda r: print("Error loading data %s" % r))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''
            loads data into a remote debug server through the POST API.
            the remote server *must* have "skip" authentication configured.
            this script does not support token retrieval for google auth or
            open ID connect. `load_timeline_for_day_and_user` is the equivalent
            script for a local server and loads the data directly into the database.
            ''')

    parser.add_argument("-d", "--debug", type=int,
        help="set log level to DEBUG")

    parser.add_argument("remote_server",
        help="the remote server to load the data to")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--input_file",
        help='''
            the input json file for the user
            the user email/label is the part before the '.timeline' suffix
            so for /tmp/shankari.july-22.timeline the email is 'shankari.july-22'
        ''')
    group.add_argument("-p", "--input_prefix",
        help='''
            the directory from which to read the input json files, one per user.
            the user email/label is between the prefix and the '.timeline' suffix
            so for /tmp/filled_pop_Tour_0.timeline with prefix = '/tmp/filled_pop_",
            the email is 'Tour_0'
        ''')

    args = parser.parse_args()

    client_config = {
        "emission_server_base_url": args.remote_server,
        "register_user_endpoint": "/profile/create",
        "user_cache_endpoint": "/usercache/put"
    }

    client = escg.EmissionFakeDataGenerator(client_config)

    if args.input_file:
        regex = re.compile(r"(\S*).timeline")
        load_user(client, args.input_file, regex)
    else:
        assert args.input_prefix is not None
        regex = re.compile(r"{prefix}(\S*).timeline".format(prefix=args.input_prefix))
        matching_files = common.read_files_with_prefix(args.input_prefix)
        print("Found %d matching files for prefix %s" %
            (len(matching_files), args.input_prefix))
        for fn in matching_files:
            load_user(client, fn, regex)
            

