from django.db.models.loading import get_model
from imageserve.ismi import api

def fetch_people(text_id):
    rel = []
    text = api.fetch('get_ent', include_content="true", id=text_id)

    if not text:
        return None

    text_data = text.get('ent', None)
    target_relations = text_data.get('src_rels', None)
    if target_relations:
        related_objects = [r for r in target_relations if r['tar_oc'] == "PERSON"]
        for pers in related_objects:
            person = api.fetch('get_ent', include_content="true", id=pers['tar_id'])
            rel.append(person.get('ent', None))
    return rel

def fetch_text_people(queryset):
    for text in queryset:
        if not text.ismi_id:
            continue

        people = fetch_people(text.ismi_id)

        if not people:
            continue

        if text.people:
            text.people.clear()

        person_model = get_model('imageserve', 'Person')

        for person in people:
            person_id = person.get('id', None)
            person_name = person.get('ov', None)
            person_atts = person.get('atts', None)

            db_person = person_model.objects.filter(ismi_id=person_id)
            if db_person.exists():
                db_person.delete()

            p = person_model()
            p.text = text
            p.name = person_name
            p.ismi_id = person_id
            p.data = person
            p.save()
