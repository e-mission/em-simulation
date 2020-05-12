# standard imports
import logging
import argparse

# our imports
import emission.simulation.input as esi
import emission.simulation.generate_measurements as esgm
import emission.simulation.output as eso

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",
        help="the input file for the population",
        default="population.xml")
    parser.add_argument("--output_prefix",
        help="the directory where the output json files are stored, one per user",
        default="/tmp/filled_pop_")
    parser.add_argument("travelDate",
        help="date on which to travel")

    logging.basicConfig(level=logging.DEBUG)
    args = parser.parse_args()

    with open(args.input) as ifp:
        person_list = esi.population2personlist(ifp)
    for person in person_list:
        fake_user = esgm.FakeUser(args.travelDate, person)
        fake_user.take_trips()
        out_filename = args.output_prefix + person["@id"].replace(" ", "_") + ".timeline"
        with open(out_filename, "w") as ofp:
            eso.sync_to_file(fake_user.get_measurements(), ofp)
