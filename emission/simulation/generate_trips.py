# standard imports
import numpy as np
import scipy.stats as scistats
import datetime
import arrow 
import requests
import pykov as pk
import os
import pandas as pd
import haversine as hs
import itertools
import logging

# our imports
import emission.simulation.transition_prob as estp

class FakeUser:
    """
    Fake user class used to generate synthetic data.
    """
#TODO: Make FakeUser an abstract class and create a concrete implementation called EmissionFakeUser
    def __init__(self, nTrips, tour_config):
        self._nTrips = nTrips
        self._tour_config = tour_config
        self._current_state = tour_config['initial_state']
        self._elapsed_mins = 0
        self._path = [self._current_state]

        self._markov_model = create_markov_model(tour_config)
        self._label_to_coordinate_dict = create_label_to_coordinate_dict(tour_config)
        self._dist_matrix = create_dist_matrix(tour_config)
        # 2-D matrix where the labels are the activities (e.g. home, work)
        # and each entry is a dict of possible modes for that activity transition
        # mode dict is mode_name -> weight
        self._possible_mode_matrix = calculate_possible_modes(tour_config, self._dist_matrix)
        # 2-D matrix where the labels are the activities (e.g. home, work)
        # and each entry is a dict of possible modes for that activity transition
        # mode dict is mode_name -> weight
        self._mode_prob_matrix = calculate_mode_prob(self._possible_mode_matrix)
        self._loc_dwell_dist = freeze_dwell_hours_random_generators(tour_config)
        self._mode_kmph_dist = freeze_mode_kmph_random_generators(tour_config)

    def take_trips(self):
        act_list = []
        self.first_dwell()
        for _ in range(self._nTrips):
            curr_act = self.take_trip()
            print('Current length of path: %d, Time elapsed = %s' %
                (len(self._path), self._elapsed_mins))
            act_list.append(curr_act)
            self.dwell()
        act_list.append(self.last_dwell())
        print('Path:', self._path)
        return act_list

    def first_dwell(self):
        initial_dwell_mins = self._freeze_first_dwell().rvs(size=1)[0] * 60
        print('>> Initially Dwelling at ', self._current_state,' for ', initial_dwell_mins, ' mins (', initial_dwell_mins/60, ') hours')
        self._elapsed_mins = self._elapsed_mins + initial_dwell_mins

    def _freeze_first_dwell(self):
        """
        The initial state is typically home, and the day starts at midnight. So
        the remaining dwell time is based on half the normal dwell time
        """
        default_dwell_frozen = self._loc_dwell_dist[self._current_state]
        default_dwell_params = {"loc": default_dwell_frozen.mean(),
            "scale": default_dwell_frozen.std()}
        first_dwell_params = {k: v/2 for k, v in default_dwell_params.items()}
        # print("first_dwell_params = %s" % first_dwell_params)
        return scistats.norm(**first_dwell_params)

    def last_dwell(self):
        curr_loc = self._current_state
        curr_coordinate = self._label_to_coordinate_dict[curr_loc]
        ret_val = {"@type": curr_loc,
            "@lat": curr_coordinate[0], "@lon": curr_coordinate[1]}
        return ret_val

    def dwell(self):
        curr_loc = self._current_state
        curr_dwell_mins = self._loc_dwell_dist[curr_loc].rvs(size=1)[0] * 60
        print('>> Dwelling at ', curr_loc,' for ', curr_dwell_mins, ' mins (', curr_dwell_mins/60, ') hours')
        self._elapsed_mins = self._elapsed_mins + curr_dwell_mins

    def take_trip(self):
        curr_loc = self._current_state
        next_loc = self._markov_model.move(self._current_state)

       #If the next location is the same as the current location, return an empty list
        if next_loc == self._current_state:
            print('>> Staying at', curr_loc)
            return None

        curr_coordinate = self._label_to_coordinate_dict[curr_loc]
        next_coordinate = self._label_to_coordinate_dict[next_loc]

        dep_date = arrow.get(self._elapsed_mins * 60)

        travel_prob_map = self._mode_prob_matrix.at[curr_loc, next_loc]
        travel_mode = estp.generate_random_mode_from_cdf(travel_prob_map)
        travel_kmph = self._mode_kmph_dist[travel_mode].rvs(size=1)[0]
        travel_mins = (self._dist_matrix.at[curr_loc, next_loc] / travel_kmph) * 60

        print('>> Traveling from', curr_loc,'to', next_loc, '| Mode of transportation:', travel_mode)
       # Here we update the current state 
       # We also update the time_object to make sure the next trip starts at a later time 
        ret_val = {"@type": curr_loc,
            "@lat": curr_coordinate[0], "@lon": curr_coordinate[1],
            "@end_time": dep_date.format("HH:mm"), "@elapsed_ts": self._elapsed_mins * 60}
        ret_val["leg"] = {}
        ret_val["leg"]["@mode"] = travel_mode
        self._elapsed_mins = self._elapsed_mins + travel_mins
        self._current_state = next_loc
        self._path.append(next_loc)
        return ret_val
    
def create_markov_model(config):
    labels = [elem['label'].lower() for elem in config['locations']]
    transition_probs = config['transition_probs']
    return estp.get_markov_chain(labels, transition_probs)

def create_label_to_coordinate_dict(config):
    locations = config['locations']
    new_dict = {}
    for loc in locations:
        new_dict[loc['label']] = tuple(loc['coordinate'])
    return new_dict

def create_dist_matrix(config):
    locations = config['locations']

    distance_df = _init_dataframe([l["label"] for l in locations])
    all_combos = itertools.product(locations, locations)
    for (sl, el) in all_combos:
        distance = hs.haversine(sl["coordinate"], el["coordinate"])
        # print("Distance between %s and %s = %s" % (sl["label"], el["label"], distance))
        distance_df.at[sl["label"], el["label"]] = distance
    return distance_df

def calculate_possible_modes(config, dist_df):
    locations = config['locations']

    mode_prob_df = _init_dataframe([l["label"] for l in locations], dtype=dict)
    all_combos = itertools.product(locations, locations)
    for (sl, el) in all_combos:
        mode_weight_map = {}
        distance = dist_df.loc[sl["label"], el["label"]]
        if distance == 0:
            mode_weight_map = None
        else:
            for (mode_label, mode_properties) in config["modes"].items():
                if "max_km" in mode_properties:
                    if mode_properties["max_km"] >= distance:
                        mode_weight_map[mode_label] = mode_properties["weight"]
                    else:
                        logging.debug("max distance %d < distance %d, skipping mode %s" %
                            (mode_properties["max_km"], distance, mode_label))
                else:
                    mode_weight_map[mode_label] = mode_properties["weight"]
        mode_prob_df.at[sl["label"], el["label"]] = mode_weight_map
    return mode_prob_df

def calculate_mode_prob(possible_mode_matrix):
    mode_prob_with_none = lambda mwm: estp.generate_mode_probs(mwm) if mwm is not None else None
    return possible_mode_matrix.applymap(mode_prob_with_none)

def _init_dataframe(loc_labels, dtype=np.float32):
    ll = len(loc_labels)
    return pd.DataFrame(np.empty((ll, ll), dtype=dtype), index = loc_labels, columns = loc_labels)

def freeze_dwell_hours_random_generators(tour_config):
    locations = tour_config['locations']
    ret_val = {}

    for loc in locations:
        ret_val[loc["label"]] = scistats.norm(**loc["dwell_hours"])
    return ret_val

def freeze_mode_kmph_random_generators(tour_config):
    modes = tour_config['modes']
    ret_val = {}

    for (mode_label, mode_details) in modes.items():
        kmph_mean = mode_details["kmph"]
        kmph_std = kmph_mean * 0.25
        ret_val[mode_label] = scistats.norm(loc=kmph_mean, scale=kmph_std)
    return ret_val
