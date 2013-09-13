from imageserve.ismi.api import fetch


def fetch_witnesses(ismi_id):
    """ Fetches witnesses for a given ID """
    rel = []
    witnesses = fetch('get_ent', include_content="true", id=ismi_id)
    if not witnesses:
        return None
    witnesses = witnesses.get('ent', None)
    target_relations = witnesses.get('tar_rels', None)
    if target_relations:
        related_objects = [r for r in target_relations if r['name'] == 'is_part_of']
        for wit in related_objects:
            witness = fetch('get_ent', include_content="true", id=wit['src_id'])
            rel.append(witness.get('ent', None))
    return rel
