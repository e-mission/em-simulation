from abc import ABC, abstractmethod
from emission.simulation.error import AddressNotFoundError
import requests

class Client(ABC):
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def register_fake_user(self, email):
        pass 

    @abstractmethod
    def sync_data_to_server(self, measurements, success_callback, failure_callback):
        pass  

class EmissionFakeDataGenerator(Client):
    def __init__(self, config):
        #TODO: Check that the config object has keys: emission_server_base_url, register_user_endpoint, user_cache_endpoint
        config["register_url"] = config['emission_server_base_url'] + config['register_user_endpoint'] 
        config["upload_url"] = config['emission_server_base_url'] + config['user_cache_endpoint'] 
        self._config = config

    def register_fake_user(self, email):
        data = {'user': email}
        url = self._config['register_url']
        r = requests.post(url, json=data)
        r.raise_for_status()
        uuid = r.json()['uuid']
        #TODO: This is a hack to make all the genereated entries JSON encodeable. 
        #Might be a bad Idead to stringify the uuid. For instance, 
        # the create_entry function expects uuid of type UUID
        return str(uuid)

    def _parse_user_config(self, config):
        #TODO: This function shoudl be used to parser user config object and check that the paramaters are valid.
        try: 
            locations = config['locations']
        except KeyError:
            print("You must specify a set of addresses")
            raise AddressNotFoundError

        #check that all addresses are supported by the trip planner software
        #for address in addresses:
        #    if not self._trip_planer_client.has_address(address):
        #        message = ("%s, is not supported by the Trip Planer", address) 
        #        raise AddressNotFoundError(message, address)

        #check that all teh transition probabilites for every address adds up to one

    @staticmethod
    def _remove_id_field(entry):
        munged = entry.copy()
        del munged['_id']
        if 'user_id' in munged:
            del munged['user_id']
        if 'write_local_dt' in munged['metadata']:
            del munged['metadata']['write_local_dt']
        if 'type' not in munged['metadata']:
            munged['metadata']['type'] = "sensor-data"
        return munged

    def sync_data_to_server(self, email, measurements, success_callback, failure_callback):
        #Remove the _id field
        #measurements_no_id = [self._remove_id_field(entry) for entry in measurements]
        measurements_no_id = measurements
        print(measurements_no_id[0])
        #Send data to server
        data = {
            'phone_to_server': measurements_no_id,
            'user': email
        }

        r = requests.post(self._config['upload_url'], json=data)

        #Check if sucessful
        if r.ok:
            success_callback(r)
        else:
            failure_callback(r)

