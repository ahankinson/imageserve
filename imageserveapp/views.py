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
    m = Manuscript.objects.get(id=ms_id)
    u = urlopen(JSON_INTERFACE+"method=get_ent&include_content=true&id="+str(m.ismi_id))
    md = json.loads(u.read())['ent']
    u.close()
    pth = os.path.join(conf.IMG_DIR, m.directory)
    def htmlify(s):
        post = ''
        if isinstance(s,dict):
            post += "<table class=\"table table-bordered\">"
            for key, value in s.items():
                post += "<tr><td>"+htmlify(key)+"</td><td>"+htmlify(value)+"</td></tr>"
            post += "</table>"
        elif isinstance(s,list):
            for item in s:
                post += htmlify(item)
        else:
            post += unicode(s)
        return post
        
    data = {
        'md': htmlify(md),
        'image_path': pth,
        'ms_name': m.directory,
    }
    return render(request, "templates/diva.html", data)