import re
# from urllib import quote_plus
# from django.conf import settings
# from django.http import Http404
# from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
# from django.core.paginator import PageNotAnInteger
from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer, JSONPRenderer
# from guardian.shortcuts import get_objects_for_user

from imageserve.renderers.custom_html_renderer import CustomHTMLRenderer
from imageserve.serializers.manuscript import ManuscriptSerializer
from imageserve.serializers.manuscript import PaginatedManuscriptSerializer
from imageserve.models import Manuscript
from imageserve.models import ManuscriptGroup

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [tryint(c) for c in re.split('([0-9]+)', s)]

def by_folio(obj):
    return alphanum_key(obj.folios)

class ManuscriptListHTMLRenderer(CustomHTMLRenderer):
    template_name = "manuscript/manuscript_list.html"


class ManuscriptDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "manuscript/manuscript_detail.html"


class ManuscriptList(generics.ListAPIView):
    model = Manuscript
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ManuscriptSerializer
    pagination_serializer_class = PaginatedManuscriptSerializer
    # paginate_by = 25
    renderer_classes = (JSONRenderer, JSONPRenderer, ManuscriptListHTMLRenderer)

    def get_queryset(self):
        queryset = Manuscript.objects.all()
        stabi = self.request.QUERY_PARAMS.get('stabi', None)

        if stabi is not None:
            self.request.show_stabi = True
            stabigroup = ManuscriptGroup.objects.filter(name="Stabi Codices")
            queryset = queryset.filter(manuscriptgroup__in=stabigroup)

        return queryset


class ManuscriptDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Manuscript
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ManuscriptSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, ManuscriptDetailHTMLRenderer)

# def manuscript(request, pk, witness=None):
#     """The view for displaying a specific manuscript."""
#     if request.user.is_anonymous():
#         u = User.objects.get(pk=-1)  # select the "AnonymousUser" object
#     else:
#         u = request.user

#     # We break the response down into a couple steps here.
#     # First, check the number of manuscripts groups they have permissions to. This is just to
#     # be able to exit with a 404 if they're trying to access a manuscript in a group that doesn't exist.

#     # Then, we check against the manuscripts themselves. This allows us to catch the user and redirect them
#     # to a log in page if they need to log in to see the MSS.
#     manuscript_groups = get_objects_for_user(u, 'imageserve.view_manuscript_group')
#     manuscripts = Manuscript.objects.filter(manuscriptgroup__in=manuscript_groups).distinct()
#     if not manuscripts.exists():
#         raise Http404

#     has_permission = manuscripts.filter(ismi_id=pk)

#     if manuscripts and not has_permission.exists():
#         return redirect('/login/?next={0}'.format(request.path))

#     m = has_permission[0]

#     known_witnesses = list(m.known_witnesses.all())
#     known_witnesses.sort(key=by_folio)

#     unknown_witnesses = list(m.unknown_witnesses.all())
#     unknown_witnesses.sort(key=by_folio)
#     has_data = False

#     data = {
#         'manuscript': m,
#         'has_data': has_data,
#         'divaserve_url': settings.DIVASERVE_URL,
#         'iipserver_url': settings.IIPSERVER_URL,
#         'image_root': settings.IMG_DIR,
#         'known_witnesses': known_witnesses,
#         'unknown_witnesses': unknown_witnesses
#         # 'ms_title': m.ms_name,
#         # 'witnesses': bool(wits),
#         # 'divaserve_url': settings.DIVASERVE_URL,
#         # 'iipserver_url': settings.IIPSERVER_URL,
#         # 'image_root': settings.IMG_DIR,
#         # # 'curr_wit': curr_wit,
#         # 'ms_name': m.directory,
#         # 'titles': titles,
#         # 'ismi_data': ismi_data,
#         # 'ms_id': manuscript,
#         # 'ismi_id': m.ismi_id,
#         # 'path': quote_plus(request.get_full_path()),
#         # 'num_files': m.num_files,
#     }
#     return render(request, "templates/diva.html", data)