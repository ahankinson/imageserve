import os
import conf
from json import dumps
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import smart_text
from divaserve import tryint, alphanum_key
from imageserveapp import img_server, JSON_INTERFACE, get_by_ismi_id
from imageserveapp.models import Manuscript, AttDisplaySetting, RelDisplaySetting

def main(request):
    """The main view, where users can browse available manuscripts."""
    manuscripts = Manuscript.objects.all()
    data = {'manuscripts': manuscripts}
    return render(request, "templates/index.html", data)

def diva(request):
    """View for divaserve"""
    msdir = request.GET.get('d')
    js = img_server.getc(msdir)
    return HttpResponse(dumps(js), content_type="application/json")

def canvas(request):
    pass

def manuscript(request, ms_id):
    """The view for displaying a specific manuscript."""
    m = Manuscript.objects.get(id=ms_id)
    entity = get_by_ismi_id(m.ismi_id)
    rl = [r for r in entity['src_rels'] if r['name'] == 'is_exemplar_of'][0]
    text = get_by_ismi_id(rl['tar_id'])
    pth = os.path.join(conf.IMG_DIR, m.directory)
    def htmlify(s):
        """
        This is a hacky way of turning an "arbitrary" Python object
        into HTML. The point is to make the metadata dict into a nice
        table which can be displayed in the "Metadata" modal.
        """
        post = ''
        if isinstance(s,dict):
            post += u"<table class=\"table table-bordered\">"
            for key, value in s.items():
                post += u"<tr><td>{0}</td><td>{1}</td></tr>".format(htmlify(key), htmlify(value))
            post += u"</table>"
        elif isinstance(s,list):
            for item in s:
                post += htmlify(item)
        else:
            post += unicode(s)
        return post
    def get_keyval(setting):
        att_name = setting.name
        key = setting.display_name
        ent = entity
        val = ''
        if not setting.on_ent:
            ent = text
        if isinstance(setting, RelDisplaySetting):
            hits = [r for r in ent[setting.rel_type+"_rels"]
                    if r['name'] == att_name]
            if hits:
                rel = hits[0]
                opp = 'tar' if setting.rel_type == 'src' else 'src'
                ent = get_by_ismi_id(rel[opp+"_id"])
                att_name = 'ov'
                if setting.show_id:
                    val = " (ID {0:n})".format(ent['id'])
        if ent.get(att_name):
            val = ent.get(att_name) + val
        else:
            hits = [a for a in ent['atts'] if a['name'] == att_name]
            if hits:
                if hits[0].get('ov'):
                    val = hits[0].get('ov') + val
        if not val:
            val = 'Data missing'
        return (key, val)
    ms_title = get_keyval(RelDisplaySetting.objects.get(name='is_exemplar_of'))[1]
    ms_author = get_keyval(RelDisplaySetting.objects.get(name='was_created_by'))[1]
    title = u'{0}<br /><br />Author: {1}'.format(ms_title, ms_author)
    md = dict([get_keyval(a) for a in AttDisplaySetting.objects.filter(show=True)]+
              [get_keyval(r) for r in RelDisplaySetting.objects.filter(show=True)])
    data = {
        'md': htmlify(md),
        'image_path': pth,
        'ms_name': m.directory,
        'title': title,
    }
    return render(request, "templates/diva.html", data)