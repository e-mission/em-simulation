# standard imports
import numpy as np
import datetime
import arrow 
import requests
import pykov as pk
import os
import logging

# our imports
import emission.simulation.transition_prob as estp
import emission.net.ext_service.otp.otp as otp

class FakeUser:
    """
    Fills in the measurements for individual user tours
    Tour consists of a sequence of places (with end times) and trips (with modes)
    """

    def __init__(self, tour_date, person):
        self._tour_date = tour_date
        self._measurements_cache = []
        self._tour = person["plan"]["act"]
        self._tour_place_pairs = zip(self._tour, self._tour[1:])
        self._otp_stub = otp.OTP(os.environ["OTP_SERVER"])

    def take_trips(self):
        for (start_place, end_place) in self._tour_place_pairs:
            print(str(start_place) + " ----------> "+str(end_place))
            measurements = self.take_trip(start_place, end_place)
            self._measurements_cache += measurements

    def get_measurements(self):
        return self._measurements_cache

    def take_trip(self, start_place, end_place):
        start_loc = (float(start_place["@lat"]), float(start_place["@lon"]))
        end_loc = (float(end_place["@lat"]), float(end_place["@lon"]))
        # Do we always have exactly one mode? assuming that is true for now...
        mode = start_place["leg"]["@mode"].upper()
        start_date = self._tour_date
        start_time = start_place["@end_time"]
        logging.info(">> Traveling from %s to %s at %sT%s | Mode of transportation %s"
            % (start_loc, end_loc, start_date, start_time, mode))
        trip_planner_client = self._otp_stub.route(start_loc, end_loc, mode,
            start_date, start_time, bike=True)
        measurements = trip_planner_client.get_measurements_along_route()
        logging.info("Got %d measurements" % len(measurements))
        return measurements
