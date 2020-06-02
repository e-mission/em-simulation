import json
import xmltodict

import emission.simulation.client as esc

def sync_to_file(measurement_list, fp):
    measurements_no_id = [esc.EmissionFakeDataGenerator._remove_id_field(entry) for entry in measurement_list]
    json.dump(measurements_no_id, fp, indent=2)

def sync_to_server(measurement_list, client):
    pass

def personlist2population(pop_xml_fp, person_id, action_list):
    pop_all = {"plans":
        {"person": {"@id": person_id, "@student": "no", "@employed": "yes"}
    }}
    pop_all["plans"]["person"]["plan"] = {"@selected": "yes", "act": action_list}
    # pop_all["plans"]["person"]["plan"] = action_list
    up = xmltodict.unparse(pop_all, pretty=True)
    with open(pop_xml_fp, "w") as ofp:
        ofp.write(up)
