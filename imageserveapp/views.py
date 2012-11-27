import os
import conf
from json import dumps
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import smart_text
from divaserve import tryint, alphanum_key
from imageserveapp import img_server, JSON_INTERFACE, get_by_ismi_id
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
    return HttpResponse(dumps(js), content_type="application/json")

def canvas(request):
    pass

def manuscript(request, ms_id):
    """The view for displaying a specific manuscript."""
    m = Manuscript.objects.get(id=ms_id)
    ent = get_by_ismi_id(m.ismi_id)
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
    ms_title = m.title()
    ms_author = m.author()
    title = u'{0}<br /><br />Author: {1}'.format(ms_title, ms_author)
    md = {
        'Title': ms_title,
        'Author': ms_author,
        'Attributes': {
            att['name']: att.get('ov') for att in ent['atts']
        },
        'Source Relations': {
            rel['name']: get_by_ismi_id(rel['tar_id']).get('ov') for rel in ent['src_rels']
        },
        'Target Relations': {
            rel['name']: get_by_ismi_id(rel['src_id']).get('ov') for rel in ent['tar_rels']
        },
    }
    data = {
        'md': htmlify(md),
        'image_path': pth,
        'ms_name': m.directory,
        'title': title,
    }
    return render(request, "templates/diva.html", data)