import os
import conf
from json import dumps
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import SafeString
from django.template import Template, Context
from imageserve import img_server
from imageserve.helpers import get_keyval
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

def metadata(request):
    """
    This view is intended to handle AJAX requests for metadata from the
    manuscript viewer page.
    """
    w = request.GET['wit_id']
    table_template = Template('''<table class="table table-bordered">
      {% for key, val in md %}
        <tr><td>{{key}}</td><td>{{val}}</td></tr>
      {% endfor %}
    </table>''')
    md = [get_keyval(a, w) for a in AttDisplaySetting.objects.filter(show=True)]+\
         [get_keyval(r, w) for r in RelDisplaySetting.objects.filter(show=True)]
    table_context = Context({'md': md})
    table = table_template.render(table_context)
    ms_title = get_keyval(RelDisplaySetting.objects.get(name='is_exemplar_of'), w)[1]
    ms_author = get_keyval(RelDisplaySetting.objects.get(name='was_created_by'), w)[1]
    ta_template = Template('{{title}}<br/><br/>Author: {{author}}')
    ta_context = Context({'title': ms_title, 'author': ms_author})
    title_auth = ta_template.render(ta_context)
    data = {'table': table, 'title_auth': title_auth}
    return HttpResponse(dumps(data), mimetype="text/json")

def manuscript(request, ms_id, curr_wit=0):
    """The view for displaying a specific manuscript."""
    # TODO: use codex id's and have the feature where metadata changes
    # as you scroll through the codex to the various witnesses contained
    # therein
    m = Manuscript.objects.get(id=ms_id)
    pth = os.path.join(conf.IMG_DIR, m.directory)
    wits = eval(m.witnesses)
    if not curr_wit in range(len(wits)):
        curr_wit = 0
    w = wits[curr_wit]
    zipped = sorted(zip(wits,m.witness_pages), key=lambda t:t[1])
    witnesses = dumps([[k,v] for k,v in zipped])
    get_title = lambda w: get_keyval(RelDisplaySetting.objects.get(name='is_exemplar_of'), w)[1]
    titles = [get_title(w) for w in wits]
    data = {
        'curr_wit': curr_wit,
        'witnesses': SafeString(witnesses),
        'image_path': pth,
        'ms_name': m.directory,
        'titles': list(enumerate(titles)),
    }
    return render(request, "templates/diva.html", data)