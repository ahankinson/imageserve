from imageserve.ismi import api
from django.db.models.loading import get_model

def update_manuscripts(manuscripts):
    for manuscript in manuscripts:
        if not manuscript.ismi_id:
            continue

        fetch_entity(manuscript.ismi_id)



def fetch_entity(entity_id):
    print("Fetching {0}".format(entity_id))
    ent_ = api.fetch('get_ent', include_content="true", id=entity_id)
    # ms_ is of type CODEX
    if not ent_.get('ent', None):
        return None

    if not ent_['ent'].get('oc', None):
        print("No type! Returning.")
        return None

    db_ent, created = get_model('imageserve', 'ISMIEntity').objects.get_or_create(ismi_id=entity_id)
    if db_ent.synced:
        return None

    print("Creating relationship with ms obj")
    db_ent.synced = True
    db_ent.data=ent_['ent']
    db_ent.ismi_type = ent_['ent']['oc']
    db_ent.save()

    print("Getting other relationships")
    if not ent_['ent'].get('tar_rels', None):
        return None

    tar_rels = ent_['ent']['tar_rels']

    print("Getting target relationships")
    for rel in tar_rels:
        if not rel.get('src_id', None):
            continue
        if not rel.get('src_oc', None):
            continue

        db_ent, created = get_model('imageserve', 'ISMIEntity').objects.get_or_create(ismi_id=rel.get('src_id'))
        if not created:
            continue

        db_ent.synced = False
        db_ent.ismi_type = rel.get('src_oc')
        db_ent.ismi_id = rel.get('src_id')
        db_ent.save()

        fetch_entity(rel.get('src_id'))

    if not ent_['ent'].get('src_rels', None):
        return None

    print("Getting source relationships")
    src_rels = ent_['ent']['src_rels']
    for rel in src_rels:
        if not rel.get('tar_id', None):
            continue
        if not rel.get('tar_oc', None):
            continue

        db_ent, created = get_model('imageserve', 'ISMIEntity').objects.get_or_create(ismi_id=rel.get('tar_id'))
        if not created:
            continue

        db_ent.synced = False
        db_ent.ismi_type = rel.get('tar_oc')
        db_ent.ismi_id = rel.get('tar_id')
        db_ent.save()

        fetch_entity(rel.get('tar_id'))

