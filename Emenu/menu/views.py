from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    text = """<h1>Bienvenue sur ma première page Django</h1>"""
    return HttpResponse(text)