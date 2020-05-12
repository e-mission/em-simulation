# standard imports
import numpy as np
import datetime
import arrow 
import requests
import pykov as pk
import os

# our imports
import emission.simulation.transition_prob as estp
import emission.net.ext_service.otp.otp as otp

class FakeUser:
    """
    Fake user class used to generate synthetic data.
    """
#TODO: Make FakeUser an abstract class and create a concrete implementation called EmissionFakeUser
    def __init__(self, trajectory_start_ts, nTrips, tour_config, client):
        self._nTrips = nTrips
        self._client = client
        self._tour_config = tour_config
        self._email = tour_config['email']
        # We need to set the time of ther user in the past to that the pipeline can find the entries.
        self._time_object = trajectory_start_ts
        self._trip_planer_client = otp.OTP(os.environ["OTP_SERVER"])
        self._current_state = tour_config['initial_state']
        self._markov_model = self._create_markov_model(tour_config)
        self._path = [self._current_state]
        self._label_to_coordinate_map = self._create_label_to_coordinate_map(tour_config)
        self._trip_to_mode_map = self._create_trip_to_mode_map(tour_config)
        self._measurements_cache = []

    #
    # BEGIN: Data generation functions
    #
    def take_trips(self):
        measurements = []
        for _ in range(self._nTrips):
            temp = self.take_trip()
            print('# of location measurements:', len(temp))
            measurements.append(temp)

        print('Path:', self._path)
        len(self._measurements_cache)
        self.sync_data_to_server()
        len(self._measurements_cache)

    def take_trip(self):
        #TODO: If we have already completed a trip, we could potentially cache the location data 
        # we get from Open Trip Planner and only modify the timestamps next time we take the same trip. 
        curr_loc = self._current_state
        next_loc = self._markov_model.move(self._current_state)

       #If the next location is the same as the current location, return an empty list
        if next_loc == self._current_state:
            print('>> Staying at', curr_loc)
            return []

        curr_coordinate = self._label_to_coordinate_map[curr_loc] 
        next_coordinate = self._label_to_coordinate_map[next_loc]

        trip_planer_client = self._create_new_otp_trip(curr_coordinate, next_coordinate, curr_loc, next_loc)

        # Get the measurements along the route. This includes location entries
        # and a motion entry for each section.
       #TODO: If get_measurements_along_route returns a PathNotFound Exception, we should catch this and return an empty list(?) 
        print('>> Traveling from', curr_loc,'to', next_loc, '| Mode of transportation:', trip_planer_client.mode)
        measurements = trip_planer_client.get_measurements_along_route()

       # Here we update the current state 
       # We also update the time_object to make sure the next trip starts at a later time 
        if len(measurements) > 0:
            #print(measurements[0].metadata.write_ts)
            end_time_last_trip = measurements[-1].data.ts
            self._update_time(end_time_last_trip)
            self._current_state = next_loc
            self._path.append(next_loc)
            #Update measurements cache
            self._measurements_cache += measurements
            #TODO: if the user cache has more than 5000 entries notify the user so they can sync the data. 

        return measurements

    def add_measurements(self, entries):
        self._measurements_cache += entries

    def _create_new_otp_trip(self, curr_coordinate, next_coordinate, cur_loc, next_loc):
        try:
            mode = self._trip_to_mode_map[(cur_loc, next_loc)]
        except KeyError:
            mode = self._tour_config['default_mode']

        date = "%s-%s-%s" % (self._time_object.month, self._time_object.day, self._time_object.year)
        time = "%s:%s" % (self._time_object.hour, self._time_object.minute)
        
        #TODO: Figure out how we should set bike
        return self._trip_planer_client.route(curr_coordinate, next_coordinate, mode, date, time, bike=True)
    
    def _update_time(self, prev_trip_end_time):
        # TODO: 3 hours is an arbritrary value. Not sure what makes sense. 
        self._time_object = arrow.get(prev_trip_end_time).shift(hours=+3)
    
    def _create_markov_model(self, config):
        labels = [elem['label'].lower() for elem in config['locations']]
        transition_probs = config['transition_probs']
        return estp.get_markov_chain(labels, transition_probs)

    def _create_label_to_coordinate_map(self, config):
        locations = config['locations']
        new_map = {}
        for loc in locations:
            new_map[loc['label']] = tuple(loc['coordinate'])

        return new_map
    
    def _create_trip_to_mode_map(self, config):
        new_map = {}
        for k, v in config['modes'].items():
            for edge in v:
                new_map[tuple(edge)] = k
        return new_map

    #
    # END: Data generation functions
    #

    #
    # BEGIN: Server communication functions
    # TODO: Move this out to some kind of server-client module?
    #

    def _flush_cache(self, response):
        self._measurements_cache = []

    def _report_error(self, response):
        print("Error while saving data. Retry or use `save_cache_to_file`")
        print(response.content)

    def sync_data_to_server(self):
        self._client.sync_data_to_server(self._email,
            self._measurements_cache, self._flush_cache, self._report_error)

    def create_user(self):
        uuid = self._client.register_fake_user(self._tour_config['email'])
        self._uuid = uuid
        self._tour_config['uuid'] = uuid

    #
    # END: Server communication functions
    #
