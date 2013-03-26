import os
import conf
from json import dumps
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.safestring import SafeString
from urllib import quote_plus
from django.template import Template, Context
from django.contrib.auth.views import logout
from django.forms import ValidationError
from imageserve import img_server
from imageserve.helpers import get_keyval
from imageserve.models import Manuscript, AttDisplaySetting, RelDisplaySetting
from imageserve.settings import NO_DATA_MSG

def main(request):
    """The main view, where users can browse available manuscripts."""
    def is_authenticated(m):
        groups = m.manuscriptgroup_set.all()
        if groups:
            for group in groups:
                if group.public:
                    return True
                if group.users.all():
                    if request.user in group.users.all():
                        return True
        return False
    data = {
        'manuscripts': filter(is_authenticated, Manuscript.objects.all()),
        'title': 'Imageserve - Available Manuscripts',
        'path': quote_plus(request.get_full_path()),
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
    def adder(clss, l):
        for a in clss.objects.all():
            if a.show != clss.NEVER_SHOW:
                kv = get_keyval(a, w)
                if a.show == clss.ALWAYS_SHOW:
                    l.append(kv)
                else:
                    _, val = kv
                    if val != NO_DATA_MSG:
                        l.append(kv)
    md = []
    adder(AttDisplaySetting, md)
    adder(RelDisplaySetting, md)
    table_context = Context({'md': md})
    table = table_template.render(table_context)
    
    ms_title = get_keyval(RelDisplaySetting.objects.get(name='is_exemplar_of'), w)[1]
    ms_author = get_keyval(RelDisplaySetting.objects.get(name='was_created_by'), w)[1]
    
    data = {'table': table, 'title': ms_title, 'author': ms_author}
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
    witnesses = None
    titles = None
    ismi_data = False
    if m.ismi_id is not None:
        ismi_data = True
        if m.witnesses:
            if not curr_wit in range(len(m.witnesses)):
                curr_wit = 0
            titles = enumerate(m.witness_titles.split(','))
    data = {
        'title': 'Imageserve - Viewing {0}'.format(m.directory),
        'witnesses': bool(m.witnesses),
        'curr_wit': curr_wit,
        'image_path': pth,
        'ms_name': m.directory,
        'titles': titles,
        'ismi_data': ismi_data,
        'ms_id': ms_id,
        'path': quote_plus(request.get_full_path()),
    }
    return render(request, "templates/diva.html", data)

def logout_view(request):
    """
    Logs out the current user.
    """
    logout(request)
    next = request.GET['next']
    return redirect(next)

def get_curr_pgrnglist(request, ms_id):
    """
    Returns the PageRangeList for the Manuscript object with id
    ms_id for the current session.
    """
    if not request.session.get('pgrnglist'):
        request.session['pgrnglist'] = {}
    if not request.session['pgrnglist'].get(ms_id):
        ms = Manuscript.objects.get(id=ms_id)
        request.session['pgrnglist'][ms_id] = \
            ms.witness_pages
    pgrnglist = request.session['pgrnglist'][ms_id]
    return pgrnglist

def set_curr_pgrnglist(request, ms_id, pgrnglist):
    """
    Modifies the PageRangeList for the Manuscript object with id
    ms_id for the current session.
    """
    if not request.session.get('pgrnglist'):
        request.session['pgrnglist'] = {}
    request.session['pgrnglist'][ms_id] = pgrnglist
    request.session.modified = True

def wit_for_page(request):
    """
    Gives the index of the current witness given the current
    Manuscript and current page in it. If no witness is specified
    for the given page, returns -1.
    """
    ms_id = int(request.GET.get('ms_id'))
    page = int(request.GET.get('page'))
    ms = Manuscript.objects.get(id=ms_id)
    for i, pg_range in enumerate(ms.witness_pages):
        if pg_range.first <= page and page <= pg_range.last:
            return HttpResponse(dumps(i), mimetype="text/json")
    return HttpResponse(dumps(-1), mimetype="text/json")

def page_for_wit(request):
    """
    Given a Manuscript id and the index of a witness in it,
    returns the first (or with the optional `last` parameter,
    last) page of that witness.
    """
    last = request.GET.get('last')
    ms_id = int(request.GET.get('ms_id'))
    wit = int(request.GET.get('wit'))
    if last:
        ret = get_curr_pgrnglist(request, ms_id)[wit].last
    else:
        ret = get_curr_pgrnglist(request, ms_id)[wit].first
    return HttpResponse(dumps(ret), mimetype="text/json")

def id_for_wit(request):
    """
    Given a Manuscript id and the index of a witness in it,
    returns the ISMI id of the corresponding WITNESS object.
    """
    ms_id = int(request.GET.get('ms_id'))
    wit = int(request.GET.get('wit'))
    ms = Manuscript.objects.get(id=ms_id)
    ret = ms.witnesses[wit]
    return HttpResponse(dumps(ret), mimetype="text/json")

def set_page(request, first_last):
    """
    In the page number editing mode, changes the first or
    last page of a witness in a given manuscript.
    """
    ms_id = int(request.GET.get('ms_id'))
    page = int(request.GET.get('page'))
    wit = int(request.GET.get('wit'))
    wit_pgs = get_curr_pgrnglist(request, ms_id)
    setattr(wit_pgs[wit], first_last, page)
    set_curr_pgrnglist(request, ms_id, wit_pgs)
    return HttpResponse()

def save_pages(request):
    """
    Saves the session-scope PageRangeList for the Manuscript
    with id `ms_id` to the database.
    """
    ms_id = int(request.GET.get('ms_id'))
    ms = Manuscript.objects.get(id=ms_id)
    pgrnglist = get_curr_pgrnglist(request, ms_id)
    try:
        ms.witness_pages = pgrnglist
        ms.clean_fields()
        ms.save()
    except ValidationError as e:
        return HttpResponse(
            dumps({"success":False, "error":str(e)}),
            mimetype="text/json"
        )
    return HttpResponse(dumps({"success": True}), mimetype="text/json")