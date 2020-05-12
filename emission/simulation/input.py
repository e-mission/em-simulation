import xmltodict

def parse_person(person_node):
    return person_node["plan"]["act"]

def population2personlist(pop_xml_fp):
    """
    Each person in the list has attributes. The person's tour is a list at
    ["plan"]["act"]  with the XML attributes as fields - e.g. person[0][1]["@lat"]
    is the latitude of the second activity for the first person.
    """
    pop_all = xmltodict.parse(pop_xml_fp.read())
    person_list = []
    return pop_all["plans"]["person"]
