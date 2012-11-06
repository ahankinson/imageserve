import os
import conf
import json
from django.http import HttpResponse
from django.shortcuts import render
from divaserve import tryint, alphanum_key
from imageserveapp import img_server
from imageserveapp.models import Manuscript


def main(request):
    """The main view, where users can browse available manuscripts."""
    ms_info = {}
    ms = os.listdir(conf.IMG_DIR)
    ms.sort(key=alphanum_key)
    ms_info = ((m.directory,m.num_files) for m in Manuscript.objects.all())
    data = {'info': ms_info}
    return render(request, "templates/index.html", data)

def diva(request):
    """View for divaserve"""
    msdir = request.GET.get('d')
    js = img_server.getc(msdir)
    return HttpResponse(json.dumps(js), content_type="application/json")

def canvas(request):
    pass

def manuscript(request, msdir):
    """The view for displaying a specific manuscript."""
    pth = os.path.join(conf.IMG_DIR, msdir)
    data = {
        'image_path': pth,
        'ms_name': msdir,
    }
    return render(request, "templates/diva.html", data)