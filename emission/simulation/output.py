import json

def sync_to_file(measurement_list, fp):
    json.dump(measurement_list, fp, indent=2)

def sync_to_server(measurement_list, client):
    pass
