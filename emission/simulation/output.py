import json

import emission.simulation.client as esc

def sync_to_file(measurement_list, fp):
    measurements_no_id = [esc.EmissionFakeDataGenerator._remove_id_field(entry) for entry in measurement_list]
    json.dump(measurements_no_id, fp, indent=2)

def sync_to_server(measurement_list, client):
    pass
