# standard imports
import logging
import argparse
import json
import random

# our imports
import emission.simulation.client as esc
import emission.simulation.transition_prob as estp

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
    parser.add_argument("--api_conf",
        help="the configuration for the client",
        default=["conf/api.conf", "conf/api.conf.sample"])
    parser.add_argument("--tour_conf",
        help="the configuration for the user's tour",
        default=["conf/tour.conf", "conf/tour.conf.sample"])
    parser.add_argument("--generate_random_prob",
        help="generate a random transition probability matrix",
        action='store_true')
    parser.add_argument("--seed",
        help="the random seed, for greater reproducibility",
        default=None)
    parser.add_argument("travelDate",
        help="date on which to travel")
    parser.add_argument("nTrips",
        help="number of trips to generate")

    logging.basicConfig(level=logging.DEBUG)
    args = parser.parse_args()

    api_conf = get_config(args.api_conf)
    print(api_conf)
    tour_conf = get_config(args.tour_conf)
    print(tour_conf)

    if args.seed is not None:
        random.seed(args.seed)
    if args.generate_random_prob:
        assert "transition_probs" not in tour_conf,\
            "Randomized probabilities will overwrite values in config file"
        n_labels = len(tour_conf["locations"])
        tour_conf["transition_probs"] = estp.generate_random_transition_prob(n_labels)

    client = esc.EmissionFakeDataGenerator(api_conf)
    fake_user = client.create_fake_user(tour_conf)

    measurements = []
    for _ in range(args.nTrips):
        temp = fake_user.take_trip()
        print('# of location measurements:', len(temp))
        measurements.append(temp)

    print('Path:',fake_user._path)
    len(fake_user._measurements_cache)
    fake_user.sync_data_to_server()
    len(fake_user._measurements_cache)
