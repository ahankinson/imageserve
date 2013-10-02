from django.db.models.loading import get_model
from imageserve.ismi import api


class ISMIWitness(object):
    """ Used to convert a dict (or a JSON representation)
        into an object. This makes it easier to use in
        Django templates.
    """
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)


def fetch_witnesses(ismi_id):
    """ Fetches witnesses for a given ISMI ID """
    rel = []
    codex = api.fetch('get_ent', include_content="true", id=ismi_id)
    if not codex:
        return None
    codex_data = codex.get('ent', None)
    target_relations = codex_data.get('tar_rels', None)
    if target_relations:
        related_objects = [r for r in target_relations if r['name'] == 'is_part_of']
        for wit in related_objects:
            witness = api.fetch('get_ent', include_content="true", id=wit['src_id'])
            rel.append(witness.get('ent', None))
    return rel


def fetch_mss_witnesses(queryset):
    """ 
        Takes a queryset of Manuscript groups and updates
        the witnesses for them.
    """
    for mss in queryset:
        if not mss.ismi_id:
            continue

        witnesses = fetch_witnesses(mss.ismi_id)

        if not witnesses:
            continue

        if mss.witnesses:
            mss.witnesses.clear()

        witness_model = get_model('imageserve', 'Witness')
        for witness in witnesses:
            wit_id = witness.get('id', None)
            wit_name = witness.get('ov', None)
            wit_atts = witness.get('atts', None)

            folios = None
            for attribute in wit_atts:
                if attribute['name'] == "folios":
                    folios = __get_folio_nums(attribute)

            db_witness = witness_model.objects.filter(ismi_id=wit_id)
            if db_witness.exists():
                db_witness.delete()

            w = witness_model()
            w.manuscript = mss
            w.folios = folios
            w.name = wit_name
            w.ismi_id = wit_id
            w.data = witness
            w.save()


def __get_folio_nums(attribute):
    if attribute.get('ov', None):
        return attribute['ov']
    return None