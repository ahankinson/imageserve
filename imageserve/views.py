import os
import re
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
from imageserve.helpers import get_keyvals, get_folios, get_att, get_rel
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
    ms_title, = get_rel(w, 'is_exemplar_of')
    ms_author, = get_rel(w, 'was_created_by')
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
                        val, = vals
                        if val == NO_DATA_MSG:
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
            titles = enumerate(get_rel(w, 'is_exemplar_of')[0] for w in m.witnesses)
    
    data = {
        'title': 'Viewing {0}'.format(m.directory),
        'witnesses': bool(m.witnesses),
        'divaserve_url': DIVASERVE_URL,
        'iipserver_url': IIPSERVER_URL,
        'image_root': pth,
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


def get_curr_folio_pgs(request):
    """
    Returns the PageRangeList for the Manuscript object with id
    ms_id for the current session.
    """
    ms_id = int(request.GET.get('ms_id'))
    if not request.session.get('folio_pgs'):
        request.session['folio_pgs'] = {}
    if not request.session['folio_pgs'].get(ms_id):
        ms = Manuscript.objects.get(id=ms_id)
        request.session['folio_pgs'][ms_id] = \
            ms.folio_pgs
    folio_pgs = request.session['folio_pgs'][ms_id]
    return folio_pgs


@login_required
def set_curr_folio_pgs(request, ms_id, folio_pgs):
    """
    Modifies the PageRangeList for the Manuscript object with id
    ms_id for the current session.
    """
    if not request.session.get('folio_pgs'):
        request.session['folio_pgs'] = {}
    request.session['folio_pgs'][ms_id] = folio_pgs
    request.session.modified = True


def folio_for_page(request):
    """
    Given the id of a Manuscript and a page number, returns
    the first folio number on the specified page.
    """
    page = int(request.GET.get('page'))
    folio_pgs = get_curr_folio_pgs(request)
    folio = folio_pgs.get_folio(page)
    return HttpResponse(dumps(folio), mimetype="text/json")


def page_for_folio(request):
    """
    Given the id of a Manuscript and a folio number, returns
    the first page with the given folio number.
    """
    folio = request.GET.get('folio')
    folio_pgs = get_curr_folio_pgs(request)
    page = folio_pgs.get_page(folio)
    return HttpResponse(dumps(page), mimetype="text/json")


def wit_for_page(request):
    """
    Gives the ISMI ID of the current witness given the current
    Manuscript and current page in it. If no witness is specified
    for the given page, returns -1.
    """
    ms_id = int(request.GET.get('ms_id'))
    page = int(request.GET.get('page'))
    ms = Manuscript.objects.get(id=ms_id)
    for w in ms.witnesses:
        folio_pgs = get_curr_folio_pgs(request)
        first, last = map(folio_pgs.get_page, get_folios(w))
        if first <= page and page <= last:
            return HttpResponse(dumps(w), mimetype="text/json")
    return HttpResponse(dumps(-1), mimetype="text/json")


def page_for_wit(request):
    """
    Given a Manuscript id and the ISMI ID of a witness in it,
    returns the first page of that witness.
    """
    wit = int(request.GET.get('wit'))
    folio, _ = get_folios(wit)
    folio_pgs = get_curr_folio_pgs(request)
    page = folio_pgs.get_page(folio)
    return HttpResponse(dumps(page), mimetype="text/json")


@login_required
def set_page(request, first_last):
    """
    In the page number editing mode, changes the first or
    last page of a witness in a given manuscript.
    """
    ms_id = int(request.GET.get('ms_id'))
    page = int(request.GET.get('page'))
    wit = int(request.GET.get('wit'))
    wit_pgs = get_curr_folio_pgs(request, ms_id)
    setattr(wit_pgs[wit], first_last, page)
    set_curr_folio_pgs(request, ms_id, wit_pgs)
    return HttpResponse()


@login_required
def save_pages(request):
    """
    Saves the session-scope PageRangeList for the Manuscript
    with id `ms_id` to the database.
    """
    ms_id = int(request.GET.get('ms_id'))
    ms = Manuscript.objects.get(id=ms_id)
    folio_pgs = get_curr_folio_pgs(request, ms_id)
    try:
        ms.witness_pages = folio_pgs
        ms.clean_fields()
        ms.save()
    except ValidationError as e:
        return HttpResponse(
            dumps({"success": False, "error": str(e)}),
            mimetype="text/json"
        )
    return HttpResponse(dumps({"success": True}), mimetype="text/json")
