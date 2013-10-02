from django.contrib.auth.views import logout
from django.shortcuts import redirect


def logout_view(request):
    """
    Logs out the current user.
    """
    logout(request)
    next = request.GET['next']
    return redirect(next)
