from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, 'index.html')


def add(request, a, b):
    if request.is_ajax():
        ajax_string = 'ajax request: '
    else:
        ajax_string = 'not ajax request: '
    c = int(a) + int(b)
    r = HttpResponse(ajax_string + str(c))
    return r
