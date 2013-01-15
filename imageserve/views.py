import os
import conf
from json import dumps
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import smart_text
from divaserve import tryint, alphanum_key
from imageserve import img_server, JSON_INTERFACE, get_by_ismi_id, get_rel_endpoint
from imageserve.models import Manuscript, AttDisplaySetting, RelDisplaySetting

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
    # TODO: use codex id's and have the feature where metadata changes
    # as you scroll through the codex to the various witnesses contained
    # therein
    m = Manuscript.objects.get(id=ms_id)
    pth = os.path.join(conf.IMG_DIR, m.directory)
    def get_keyval(setting):
        key = setting.display_name
        val = setting.get_val(m.ismi_id)
        return (key, val)
    ms_title = get_keyval(RelDisplaySetting.objects.get(name='is_exemplar_of'))[1]
    ms_author = get_keyval(RelDisplaySetting.objects.get(name='was_created_by'))[1]
    md = [get_keyval(a) for a in AttDisplaySetting.objects.filter(show=True)]+\
         [get_keyval(r) for r in RelDisplaySetting.objects.filter(show=True)]
    data = {
        'md': md,
        'image_path': pth,
        'ms_name': m.directory,
        'title': ms_title,
        'author': ms_author
    }
    return render(request, "templates/diva.html", data)