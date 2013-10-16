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
    permission_classes = (permissions.DjangoObjectPermissions,)
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
    permission_classes = (permissions.DjangoObjectPermissions,)
    serializer_class = ManuscriptSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, ManuscriptDetailHTMLRenderer)
