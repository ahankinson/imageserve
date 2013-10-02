import json
import os
from django.contrib.auth.models import User
from guardian.shortcuts import get_objects_for_user
from imageserve.models import Manuscript
from django.http import HttpResponse


def search(request):
    if request.user.is_anonymous():
        u = User.objects.get(pk=-1)  # select the "AnonymousUser" object
        show_all = False
    else:
        u = request.user
        show_all = request.GET.get('show_all', False)
        if show_all:
            show_all = bool(int(show_all))

    manuscript_groups = get_objects_for_user(u, 'imageserve.view_manuscript_group')
    # msf = Manuscript.objects.filter(manuscriptgroup__in=manuscript_groups)

    q = request.GET.get('q', None)
    m = Manuscript.objects.filter(directory__icontains=q, manuscriptgroup__in=manuscript_groups).distinct()

    js = [(j.ismi_id, os.path.basename(j.directory)) for j in m]
    return HttpResponse(json.dumps(js), content_type="application/json")


def goto(request):
    q = request.GET.get('q', None)
    m = Manuscript.objects.get(directory=q)
    return HttpResponse(json.dumps({'codex': m.id}), content_type="application/json")
