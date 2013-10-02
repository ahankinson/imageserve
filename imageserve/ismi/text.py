from django.db.models.loading import get_model
from imageserve.ismi import api

import pdb


def fetch_texts(witness_id):
    # fetches texts for a given witness_id
    rel = []
    witness = api.fetch('get_ent', include_content="true", id=witness_id)
    if not witness:
        return None

    witness_data = witness.get('ent', None)
    source_relations = witness_data.get('src_rels', None)

    if source_relations:
        related_objects = [r for r in source_relations if r['tar_oc'] == "TEXT"]
        for text in related_objects:
            text = api.fetch('get_ent', include_content="true", id=text['tar_id'])
            rel.append(text.get('ent', None))
    return rel

def fetch_witness_texts(queryset):
    for witness in queryset:
        if not witness.ismi_id:
            continue

        texts = fetch_texts(witness.ismi_id)

        if witness.texts:
            witness.texts.clear()

        text_model = get_model('imageserve', 'Text')

        for text in texts:
            text_id = text.get('id', None)
            text_name = text.get('ov', None)
            text_atts = text.get('atts', None)

            db_text = text_model.objects.filter(ismi_id=text_id)

            if db_text.exists():
                db_text.delete()

            t = text_model()
            t.witness = witness
            t.name = text_name
            t.ismi_id = text_id
            t.data = text
            t.save()
