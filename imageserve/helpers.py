import os
from urllib import urlopen
from json import loads
from imageserve.settings import JSON_INTERFACE, NO_DATA_MSG
from imageserve.conf import IMG_DIR
from django.core.cache import cache


def get_keyval(setting, iden):
    """
    Given an AttSetting or a RelSetting object and an ISMI ID for a
    WITNESS, return the name and value of that att or rel for the
    given witness.
    """
    key = setting.display_name
    try:
        val = setting.get_val(iden)
    except:
        val = NO_DATA_MSG
    return (key, val)


def get_by_ismi_id(iden):
    """
    Given a valid ISMI database id `iden`, return a Python dict containing
    all the relevant info from the ISMI database entity corresponding to
    that id.
    """
    ent = cache.get(iden)
    if ent is None:
        u = urlopen(
            JSON_INTERFACE+"method=get_ent&include_content=true&id="+str(iden)
        )
        s = u.read()
        ent = loads(s)['ent']
        u.close()
        cache.set(iden, ent)
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


def register_defs():
    """
    Gets all the relevant definitions for attributes and relations
    from the ISMI database and creates Setting objects for them.
    """
    from imageserve.models import AttDisplaySetting, RelDisplaySetting
    u = urlopen(JSON_INTERFACE+"method=get_defs")
    defs = loads(u.read())['defs']
    u.close()
    witness_def = [d for d in defs if d.get('ov') == 'WITNESS'][0]
    text_def = [d for d in defs if d.get('ov') == 'TEXT'][0]

    for att in witness_def['atts']:
        if not AttDisplaySetting.objects.filter(name=att['ov']):
            sett = AttDisplaySetting(name=att['ov'], on_ent='self')
            sett.save()

    for att in text_def['atts']:
        if not AttDisplaySetting.objects.filter(name=att['ov']):
            sett = AttDisplaySetting(name=att['ov'], on_ent='is_exemplar_of')
            sett.save()

    for rel in witness_def['src_rels']:
        if not RelDisplaySetting.objects.filter(name=rel['name']) and rel['name'] != 'was_created_by':
            sett = RelDisplaySetting(name=rel['name'], on_ent='self')
            sett.save()

    for rel in text_def['src_rels']:
        if not RelDisplaySetting.objects.filter(name=rel['name']):
            sett = RelDisplaySetting(name=rel['name'], on_ent='is_exemplar_of')
            sett.save()

    for rel in witness_def['tar_rels']:
        if not RelDisplaySetting.objects.filter(name=rel['name']):
            sett = RelDisplaySetting(name=rel['name'], on_ent='self')
            sett.save()

    for rel in text_def['tar_rels']:
        if not RelDisplaySetting.objects.filter(name=rel['name']):
            sett = RelDisplaySetting(name=rel['name'], on_ent='is_exemplar_of')
            sett.save()


def register_manuscripts():
    """
    Looks through the IMG_DIR folder for all manuscripts and ensures the
    database contains a Manuscript object for each.
    """
    from imageserve.models import Manuscript

    directories = os.listdir(IMG_DIR)
    known_manuscripts = Manuscript.objects.values_list('directory', flat=True)
    unknown_manuscripts = set(known_manuscripts).symmetric_difference(set(directories))
    for name in unknown_manuscripts:
        if os.path.isdir(os.path.join(IMG_DIR, name)):
            m = Manuscript(directory=name)
            m.clean()
            m.save()
