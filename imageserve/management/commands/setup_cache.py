from django.core.management.base import BaseCommand
from django.core.cache import cache
from imageserve.models import Manuscript, RelDisplaySetting
from imageserve.settings import JSON_INTERFACE, CACHE_ENABLED, NO_DATA_MSG
from imageserve.helpers import get_name
from urllib import urlopen
from json import loads

class Command(BaseCommand):
    help = 'Set up the cache so that all the relation data is set'

    def handle(self, *args, **options):
        all_rels = {}
        ocs = []
        for r in RelDisplaySetting.objects.all():
            print u'retrieving {0} relations...'.format(r.name)
            u = urlopen(JSON_INTERFACE + "method=get_rels&rel_name={0}".format(r.name))
            rels = loads(u.read())['rels']
            u.close()
            d = dict((e.get('src_id'), []) for e in rels)
            for rel in rels:
                for key in ['src_oc', 'tar_oc']:
                    if key in rel:
                        if not rel[key] in ocs:
                            ocs.append(rel[key])
                d[rel.get('src_id')].append((rel.get('tar_id'), rel.get('tar_oc')))
            all_rels[r.name] = d
        objs = {}
        for oc in ocs:
            print u'retrieving {0} objects...'.format(oc)
            u = urlopen(JSON_INTERFACE + "method=get_ents&oc={0}".format(oc))
            ents = loads(u.read())['ents']
            u.close()
            objs.update(dict((e['id'], get_name(e)) for e in ents))
            del ents
        print 'compiling connections...'
        mapper = {}
        for m in Manuscript.objects.all():
            for w in m.witnesses:
                mapper[w] = {}
                for r in RelDisplaySetting.objects.all():
                    if r.on_ent == u'self':
                        want_id = w
                    else:
                        print r.name, r.on_ent
                        if w in all_rels[r.on_ent].keys():
                            (want_id, _), = all_rels[r.on_ent][w]
                        else:
                            matches = [k for k,v in all_rels[r.on_ent].iteritems() if w in
                                        [i for i,c in v]]
                            if matches:
                                want_id, = matches
                            else:
                                mapper[w][r.name] = [NO_DATA_MSG]
                                continue
                    if want_id in all_rels[r.name].keys():
                        matches = [i for i,c in all_rels[r.name][want_id]]
                    else:
                        matches = [k for k,v in all_rels[r.name].iteritems() if want_id in
                                    [i for i,c in v]]
                    if not matches:
                        mapper[w][r.name] = [NO_DATA_MSG]
                        continue
                    mapper[w][r.name] = \
                        [objs.get(get_id, NO_DATA_MSG) for get_id in matches]
        print 'updating the cache...'
        d = cache.get('rels', {})
        for wit, rels in mapper.iteritems():
            wit_dict = d.get(wit, {})
            for r, vals in rels.iteritems():
                wit_dict[r] = vals
            d[wit] = wit_dict
        cache.set('rels', d)
