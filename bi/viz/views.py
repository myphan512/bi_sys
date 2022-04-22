from django.shortcuts import render
from django.http import HttpResponseNotFound
import os
from os import listdir


### RENDER DASHBOARD
def render_dash(request, slug):
    dashboards = [f for f in listdir((os.path.abspath(os.path.dirname(__file__)) + '\dashboards').replace('\\', '/')) if
                  f.endswith('.py')]
    if slug+'.py' not in dashboards:
        return HttpResponseNotFound('<h1>Dashboard Not Found</h1>')
    else:
        return render(request, 'viz/dashboards/'+slug+'.html')
