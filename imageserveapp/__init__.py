import divaserve
from urllib import urlopen
from json import loads

JSON_INTERFACE = "https://openmind-ismi-dev.mpiwg-berlin.mpg.de/om4-ismi/jsonInterface?"
img_server = divaserve.DivaServe()

def get_by_ismi_id(iden):
    """
    Given a valid ISMI database id `iden`, return a Python dict containing
    all the relevant info from the ISMI database entity corresponding to
    that id.
    """
    u = urlopen(JSON_INTERFACE+"method=get_ent&include_content=true&id="+str(iden))
    ent = loads(u.read())['ent']
    u.close()
    return ent

def ismi_witness_def():
    """
    Get the definition of the WITNESS object class in the ISMI database.
    This definition is serialized as a JSON object, but this method
    returns a Python dict, which contains descriptions of all the
    fields, attributes and relations which the ISMI database permits on
    a WITNESS object.
    """
    u = urlopen(JSON_INTERFACE+"method=get_defs")
    defs = loads(u.read())['defs']
    u.close()
    w = [d for d in defs if d.get('ov') == 'WITNESS'][0]
    return w

	