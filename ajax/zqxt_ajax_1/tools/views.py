from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
    
def add(request):
    a = request.GET['a']
    b = request.GET['b']
    a = int(a)
    b = int(b)
    return HttpResponse(str(a+b))
