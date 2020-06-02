# standard imports
import logging
import argparse
import json
import random
import arrow
import os

# our imports
import emission.simulation.generate_trips as esgt
import emission.simulation.transition_prob as estp
import emission.simulation.output as eso

def get_config(config_arg):
    if type(config_arg) == list:
        # the user did not override
        for fn in config_arg:
            logging.debug("Trying default file %s" % fn)
            try:
                with open(fn) as fp:
                    # we will return the first existing entry, which is what we want
                    return json.load(fp)
            except FileNotFoundError as fofe:
                logging.debug("File %s not found, trying next option..." % fn)
    else:
        assert type(config_arg) == str,\
            "unknown config file location, neither default nor user specified"
        logging.debug("Trying user specified file %s" % config_arg)
        with open(config_arg) as fp:
            return json.load(fp)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--tour_conf",
        help="the configuration for the user's tour",
        default=["conf/tour.conf", "conf/tour.conf.sample"])
    parser.add_argument("--outfile",
        help="the file to save the generated trips to",
        default="population.xml")
    parser.add_argument("--generate_random_prob",
        help="generate a random transition probability matrix",
        action='store_true')
    parser.add_argument("--seed",
        help="the random seed, for greater reproducibility",
        default=None)
    parser.add_argument("nTrips", type=int,
        help="number of trips to generate")

    logging.basicConfig(level=logging.DEBUG)
    args = parser.parse_args()

    tour_conf = get_config(args.tour_conf)
    print(tour_conf)

    if args.seed is not None:
        random.seed(args.seed)
    if args.generate_random_prob:
        assert "transition_probs" not in tour_conf,\
            "Randomized probabilities will overwrite values in config file"
        n_labels = len(tour_conf["locations"])
        tour_conf["transition_probs"] = estp.generate_random_transition_prob(n_labels)

    fake_user = esgt.FakeUser(args.nTrips, tour_conf)
    act_list = fake_user.take_trips()
    eso.personlist2population(args.outfile, tour_conf["email"], act_list)
