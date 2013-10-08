from urllib import quote_plus

from django.contrib.auth.models import User
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.views import logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from guardian.shortcuts import get_objects_for_user

from imageserve.models import Manuscript
from imageserve.models import ManuscriptGroup


# def main(request):
#     """The main view, where users can browse available manuscripts."""
#     if request.user.is_anonymous():
#         u = User.objects.get(pk=-1)  # select the "AnonymousUser" object
#         show_all = False
#     else:
#         u = request.user
#         show_all = request.GET.get('show_all', False)
#         if show_all:
#             show_all = bool(int(show_all))

#     manuscript_groups = get_objects_for_user(u, 'imageserve.view_manuscript_group')
#     msf = Manuscript.objects.filter(manuscriptgroup__in=manuscript_groups)

#     if not show_all:
#         # this assumes the existence of a manuscriptgroup called "Stabi Codices"...
#         stabi = ManuscriptGroup.objects.filter(name="Stabi Codices")
#         msf = msf.filter(manuscriptgroup__in=stabi)

#     ms = msf.distinct()
#     paginator = Paginator(ms, 25)
#     page = request.GET.get('page')

#     try:
#         manuscripts = paginator.page(page)
#     except PageNotAnInteger:
#         manuscripts = paginator.page(1)
#     except EmptyPage:
#         manuscripts = paginator.page(paginator.num_pages)

#     data = {
#         'manuscripts': manuscripts,
#         'title': 'Available Manuscripts',
#         'path': quote_plus(request.get_full_path()),
#         'show_all': show_all
#     }
#     return render(request, "templates/index.html", data)