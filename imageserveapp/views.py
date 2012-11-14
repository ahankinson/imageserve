import os
import conf
import json
from urllib import urlopen
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import smart_text
from divaserve import tryint, alphanum_key
from imageserveapp import img_server, JSON_INTERFACE
from imageserveapp.models import Manuscript


def main(request):
    """The main view, where users can browse available manuscripts."""
    manuscripts = Manuscript.objects.all()
    data = {'manuscripts': manuscripts}
    return render(request, "templates/index.html", data)

def diva(request):
    """View for divaserve"""
    msdir = request.GET.get('d')
    js = img_server.getc(msdir)
    return HttpResponse(json.dumps(js), content_type="application/json")

def canvas(request):
    pass

def manuscript(request, ms_id):
    """The view for displaying a specific manuscript."""
    def get_by_id(iden):
        u = urlopen(JSON_INTERFACE+"method=get_ent&include_content=true&id="+str(iden))
        ent = json.loads(u.read())['ent']
        u.close()
        return ent
    m = Manuscript.objects.get(id=ms_id)
    md = get_by_id(m.ismi_id)
    pth = os.path.join(conf.IMG_DIR, m.directory)
    def htmlify(s):
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
    ms_title = md['ov']
    author_id = [rel for rel in md['src_rels'] if rel['name'] == 'was_created_by'][0]['tar_id']
    ms_author = get_by_id(author_id)['ov']
    title = u'{0}<br /><br />Author: {1}'.format(ms_title, ms_author)
    better_md = {
        'Title': ms_title,
        'Author': ms_author,
        'Attributes': {
            att['name']: att.get('ov') for att in md['atts']
        },
        'Source Relations': {
            rel['name']: get_by_id(rel['tar_id']).get('ov') for rel in md['src_rels']
        },
        'Target Relations': {
            rel['name']: get_by_id(rel['src_id']).get('ov') for rel in md['tar_rels']
        },
    }
    data = {
        'md': htmlify(better_md),
        'image_path': pth,
        'ms_name': m.directory,
        'title': title,
    }
    return render(request, "templates/diva.html", data)