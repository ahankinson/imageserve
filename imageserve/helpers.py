import os
import re
import json
import urllib

from imageserve.settings import JSON_INTERFACE, NO_DATA_MSG, CACHE_ENABLED
from imageserve.conf import IMG_DIR
from django.core.cache import cache


def get_name(ent, **kwargs):
    """
    Given a dictionary representing an ISMI entity, try to find the
    most human-legible name for it possible -- failing that, return
    its ISMI ID.
    """
    show_id = False
    if 'show_id' in kwargs:
        show_id = kwargs.pop('show_id')
    ret = None
    while ret is None:
        if 'ov' in ent:
            if ent['ov']:
                ret = ent['ov']
                break
        if 'oc' in ent:
            if 'REFERENCE' == ent['oc']:
                if 'atts' in ent:
                    for att in ent['atts']:
                        if 'name' in att:
                            break_after = False
                            if 'id' == att['name']:
                                if 'ov' in att:
                                    if att['ov']:
                                        ret = att['ov']
                                        break
                            if 'endnote-content' == att['name']:
                                if 'ov' in att:
                                    if att['ov']:
                                        ret = att['ov']
                                        break_after = True
                            if break_after:
                                for attr in ent['atts']:
                                    if 'additional_information' == attr['name']:
                                        if 'ov' in attr:
                                            if attr['ov']:
                                                ret += u" {0}".format(attr['ov'])
                                        break
                                break
        if ret is None:
            return u"ISMI entity {0}".format(ent['id'])
    if show_id:
        return u"{0} (ISMI ID {1})".format(ret, ent['id'])
    return unicode(ret)


def get_keyvals(setting, iden):
    """
    Given an AttSetting or a RelSetting object and an ISMI ID for a
    WITNESS, return the name and values of that att or rel for the
    given witness.
    """
    key = setting.display_name
    try:
        vals = setting.get_vals(iden)
    except:
        vals = [NO_DATA_MSG]
    return (key, vals)


def get_by_ismi_id(iden):
    """
    Given a valid ISMI database id `iden`, returns a Python dict containing
    all the relevant info from the ISMI database entity corresponding to
    that id.
    """
    ent = None
    if CACHE_ENABLED:
        ent = cache.get(iden)

    if ent is None:
        u = urllib.urlopen(
            "{0}method=get_ent&include_content=true&id={1}"
            .format(JSON_INTERFACE, iden)
        )
        s = u.read()
        ent = json.loads(s)['ent']
        u.close()
        if CACHE_ENABLED:
            cache.set(iden, ent)

    return ent


def get_att(ismi_id, att_name):
    from imageserve.models import AttDisplaySetting
    a = AttDisplaySetting.objects.get(name=att_name)
    val, = a.get_vals(ismi_id)
    return val


def get_rel(ismi_id, rel_name):
    from imageserve.models import RelDisplaySetting
    r = RelDisplaySetting.objects.get(name=rel_name)
    vals = r.get_vals(ismi_id)
    return vals


def get_folios(wit):
    """
    Returns the folios attribute on the witness with the
    specified id.
    """
    folios = get_att(wit, 'folios')
    if folios == NO_DATA_MSG:
        return
    (first, last), = re.findall(r'(\d+[a|b]?)-(\d+[a|b]?)', folios)
    return (first, last)


def register_defs():
    """
    Gets all the relevant definitions for attributes and relations
    from the ISMI database and creates Setting objects for them.
    """
    from imageserve.models import AttDisplaySetting, RelDisplaySetting
    u = urllib.urlopen(JSON_INTERFACE+"method=get_defs")
    defs = json.loads(u.read())['defs']
    u.close()
    witness_def, = [d for d in defs if d.get('ov') == 'WITNESS']
    text_def, = [d for d in defs if d.get('ov') == 'TEXT']
    codex_def, = [d for d in defs if d.get('ov') == 'CODEX']

    for att in witness_def['atts']:
        if not AttDisplaySetting.objects.filter(name=att['ov']):
            sett = AttDisplaySetting(name=att['ov'], on_ent='self', content_type=att['content_type'], oc='WITNESS')
            sett.save()

    for att in text_def['atts']:
        if not AttDisplaySetting.objects.filter(name=att['ov']):
            sett = AttDisplaySetting(name=att['ov'], on_ent='is_exemplar_of', content_type=att['content_type'], oc='TEXT')
            sett.save()

    for att in codex_def['atts']:
        if not AttDisplaySetting.objects.filter(name=att['ov']):
            sett = AttDisplaySetting(name=att['ov'], on_ent='self', content_type=att['content_type'], oc='CODEX')
            sett.save()

    for rel in witness_def['src_rels']:
        if not RelDisplaySetting.objects.filter(name=rel['name']) and rel['name'] != 'was_created_by':
            tar_oc, = [d['ov'] for d in defs if d.get('id') == rel['tar_id']]
            sett = RelDisplaySetting(name=rel['name'], on_ent='self', src_oc='WITNESS', tar_oc=tar_oc)
            sett.save()

    for rel in text_def['src_rels']:
        if not RelDisplaySetting.objects.filter(name=rel['name']):
            sett = RelDisplaySetting(name=rel['name'], on_ent='is_exemplar_of')
            sett.save()

    for rel in codex_def['src_rels']:
        if not RelDisplaySetting.objects.filter(name=rel['name']):
            sett = RelDisplaySetting(name=rel['name'], on_ent='self')
            sett.save()

    for rel in witness_def['tar_rels']:
        if not RelDisplaySetting.objects.filter(name=rel['name']):
            sett = RelDisplaySetting(name=rel['name'], on_ent='self')
            sett.save()

    for rel in text_def['tar_rels']:
        if not RelDisplaySetting.objects.filter(name=rel['name']):
            sett = RelDisplaySetting(name=rel['name'], on_ent='is_exemplar_of')
            sett.save()

    for rel in codex_def['tar_rels']:
        if not RelDisplaySetting.objects.filter(name=rel['name']):
            sett = RelDisplaySetting(name=rel['name'], on_ent='self')
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
