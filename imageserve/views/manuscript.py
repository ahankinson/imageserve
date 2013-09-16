from urllib import quote_plus
from django.conf import settings
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.paginator import PageNotAnInteger
from guardian.shortcuts import get_objects_for_user

from imageserve.models import Manuscript

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
    except (ValueError, TypeError):
        curr_wit = -1

    # witnesses = None
    titles = None
    ismi_data = False
    wits = PageNotAnInteger

    # if m.ismi_id is not None:
    #     codex_title = get_name(get_by_ismi_id(m.ismi_id))
    #     ismi_data = True
    #     wits = m.witnesses
    #     if wits:
    #         if not curr_wit in wits:
    #             curr_wit = -1
    #         titles = [(w, get_rel(w, 'is_exemplar_of')[0], get_att(w, 'folios'))
    #                   for w in wits]
    # else:
    #     codex_title = m.directory

    ismi_data = True

    data = {
        'ms_title': m.ms_name,
        'witnesses': bool(wits),
        'divaserve_url': settings.DIVASERVE_URL,
        'iipserver_url': settings.IIPSERVER_URL,
        'image_root': settings.IMG_DIR,
        'curr_wit': curr_wit,
        'ms_name': m.directory,
        'titles': titles,
        'ismi_data': ismi_data,
        'ms_id': ms_id,
        'ismi_id': m.ismi_id,
        'path': quote_plus(request.get_full_path()),
        'num_files': m.num_files,
    }
    return render(request, "templates/diva.html", data)