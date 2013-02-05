import os
import conf
from json import dumps
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.safestring import SafeString
from django.template import Template, Context
from django.contrib.auth.views import logout
from imageserve import img_server
from imageserve.helpers import get_keyval
from imageserve.models import Manuscript, AttDisplaySetting, RelDisplaySetting

def main(request):
    """The main view, where users can browse available manuscripts."""
    def is_authenticated(m):
        groups = m.manuscriptgroup_set.all()
        if groups:
            for group in groups:
                if group.users.all():
                    if request.user not in group.users.all():
                        return False
        return True
    data = {
        'manuscripts': filter(is_authenticated, Manuscript.objects.all()),
        'title': 'Imageserve - Available Manuscripts'
    }
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

def manuscript(request, ms_id):
    """The view for displaying a specific manuscript."""
    curr_wit = request.GET.get('curr_wit')
    try:
        curr_wit = int(curr_wit)
    except:
        curr_wit = 0
    m = Manuscript.objects.get(id=ms_id)
    groups = m.manuscriptgroup_set.all()
    for group in groups:
        if group.users.all():
            if request.user not in group.users.all():
                return redirect('/login/?next=%s' % request.path)
    pth = os.path.join(conf.IMG_DIR, m.directory)
    wits = eval(m.witnesses)
    if not curr_wit in range(len(wits)):
        curr_wit = 0
    w = wits[curr_wit]
    zipped = sorted(zip(wits,m.witness_pages), key=lambda t:t[1])
    witnesses = dumps([[k,v] for k,v in zipped])
    titles = m.witness_titles.split(',')
    data = {
        'title': 'Imageserve - Viewing {0}'.format(m.directory),
        'curr_wit': curr_wit,
        'witnesses': SafeString(witnesses),
        'image_path': pth,
        'ms_name': m.directory,
        'titles': enumerate(titles),
    }
    return render(request, "templates/diva.html", data)

def logout_view(request):
    logout(request)
    return redirect('/')