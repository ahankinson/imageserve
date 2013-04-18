import os
import conf
from json import dumps
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from urllib import quote_plus
from django.contrib.auth.decorators import login_required
from django.template import Template, Context
from django.contrib.auth.views import logout
from django.forms import ValidationError
from imageserve import img_server
from imageserve.helpers import get_keyvals
from imageserve.models import Manuscript, ManuscriptGroup, AttDisplaySetting, RelDisplaySetting
from imageserve.settings import NO_DATA_MSG, DIVASERVE_URL, IIPSERVER_URL
from guardian.shortcuts import get_objects_for_user, get_perms


def main(request):
    """The main view, where users can browse available manuscripts."""
    if request.user.is_anonymous():
        u = User.objects.get(pk=-1)  # select the "AnonymousUser" object
        show_all = False
    else:
        u = request.user
        show_all = request.GET.get('show_all', False)
        if show_all:
            show_all = bool(int(show_all))
    
    manuscript_groups = get_objects_for_user(u, 'imageserve.view_manuscript_group')
    manuscripts = Manuscript.objects.filter(manuscriptgroup__in=manuscript_groups)
    if not show_all:
        # this assumes the existence of a manuscriptgroup called "Stabi Codices"...
        stabi = ManuscriptGroup.objects.filter(name="Stabi Codices")
        manuscripts = manuscripts.filter(manuscriptgroup__in=stabi)
    manuscripts = manuscripts.distinct()
    
    data = {
        'manuscripts': manuscripts,
        'title': 'Available Manuscripts',
        'path': quote_plus(request.get_full_path()),
        'show_all': show_all
    }
    return render(request, "templates/index.html", data)


def diva(request):
    """View for divaserve"""
    msdir = request.GET.get('d')
    js = img_server.getc(msdir)
    return HttpResponse(dumps(js), content_type="application/json")


def title_author(request):
    """
    This view handles AJAX requests to asynchronously update the
    Title and Author information on the viewer page.
    """
    w = request.GET['wit_id']
    ms_title = get_keyvals(RelDisplaySetting.objects.get(name='is_exemplar_of'), w)[1][0]
    ms_author = get_keyvals(RelDisplaySetting.objects.get(name='was_created_by'), w)[1][0]
    data = {'title': ms_title, 'author': ms_author}
    return HttpResponse(dumps(data), mimetype="text/json")


def metadata(request):
    """
    This view serves the metadata window.
    """
    w = int(request.GET['wit_id'])
    ms_name = request.GET['ms_name']
    
    def adder(clss, l):
        for a in clss.objects.all():
            if a.show != clss.NEVER_SHOW:
                k, vals = get_keyvals(a, w)
                if a.show == clss.ALWAYS_SHOW:
                    for val in vals:
                        l.append((k, val))
                else:
                    if len(vals) == 1:
                        if val[0] == NO_DATA_MSG:
                            continue
                    for val in vals:
                        l.append((k, val))
    
    md = []
    adder(AttDisplaySetting, md)
    adder(RelDisplaySetting, md)
    
    data = {'ms_name': ms_name, 'md': md}
    return render(request, "templates/metadata.html", data)


def manuscript(request, ms_id):
    """The view for displaying a specific manuscript."""
    if request.user.is_anonymous():
        u = User.objects.get(pk=-1)  # select the "AnonymousUser" object
    else:
        u = request.user
    
    # We break the response down into a couple steps here.
    # First, check the number of manuscripts groups they have permissions to. This is just to
    # be able to exit with a 404 if they're trying to access a manuscript in a group that doesn't exist.
    
    # Then, we check against the manuscripts themselves. This allows us to catch the user and redirect them
    # to a log in page if they need to log in to see the MSS.
    manuscript_groups = get_objects_for_user(u, 'imageserve.view_manuscript_group')
    manuscripts = Manuscript.objects.filter(manuscriptgroup__in=manuscript_groups).distinct()
    if not manuscripts.exists():
        raise Http404
    
    has_permission = manuscripts.filter(id=ms_id)
    
    if manuscripts and not has_permission.exists():
        return redirect('/login/?next={0}'.format(request.path))
    
    m = has_permission[0]
    curr_wit = request.GET.get('curr_wit')
    try:
        curr_wit = int(curr_wit)
    except:
        curr_wit = -1
    
    pth = os.path.join(conf.IMG_DIR, m.directory)
    # witnesses = None
    titles = None
    ismi_data = False
    
    if m.ismi_id is not None:
        ismi_data = True
        if m.witnesses:
            if not curr_wit in range(len(m.witnesses)):
                curr_wit = 0
            titles = enumerate(m.witness_titles.split(','))
    
    data = {
        'title': 'Viewing {0}'.format(m.directory),
        'witnesses': bool(m.witnesses),
        'divaserve_url': DIVASERVE_URL,
        'iipserver_url': IIPSERVER_URL.format(pth),
        'curr_wit': curr_wit,
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


@login_required
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


@login_required
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


@login_required
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
            dumps({"success": False, "error": str(e)}),
            mimetype="text/json"
        )
    return HttpResponse(dumps({"success": True}), mimetype="text/json")
