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

def get_rel_endpoint(ent, rel, rel_type):
    if 'src' == rel_type:
        match = [r for r in ent['src_rels'] if r['name'] == rel]
        if match:
            return get_by_ismi_id(match[0]['tar_id'])
    else:
        match = [r for r in ent['tar_rels'] if r['name'] == rel]
        if match:
            return get_by_ismi_id(match[0]['src_id'])