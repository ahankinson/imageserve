from django.shortcuts import render

def person(request, person):
    data = {}
    return render(request, "templates/person.html", data)