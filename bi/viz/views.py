from django.shortcuts import render
from django.http import HttpResponseNotFound
from .models import *
import os
from os import listdir
import importlib

### RENDER DASHBOARD LIBRARY
def render_dashboard_library(request):
    dash_list = Dashboard.objects.all()
    context = {'dash_list': dash_list}
    return render(request, 'viz/dashboards/dashboard_library.html', context)

### RENDER ABOUT PAGE
def render_about(request):
    return render(request, 'viz/about.html')


### RENDER DASHBOARD
def render_dash(request, slug):
    dashboards = [f for f in listdir((os.path.abspath(os.path.dirname(__file__)) + '\dashboards').replace('\\', '/')) if
                  f.endswith('.py')]
    if slug+'.py' not in dashboards:
        return HttpResponseNotFound('<h1>Dashboard Not Found</h1>')
    else:
        dashboard = Dashboard.objects.get(file=slug+'.py')
        context = {'dashboard':dashboard}
        return render(request, 'viz/dashboards/dashboard.html', context)


### RENDER GRAPH
def render_chart(request, slug):
    charts = [f for f in listdir((os.path.abspath(os.path.dirname(__file__)) + '\charts').replace('\\', '/')) if
                  f.endswith('.py')]
    if slug+'.py' not in charts:
        return HttpResponseNotFound('<h1>Chart Not Found</h1>')
    else:
        # import module in charts based on slug argument
        module = importlib.import_module('.charts.'+slug, package=__package__)
        context = {'graph':module.fig.to_html()}
        return render(request, 'viz/charts/chart.html', context)

