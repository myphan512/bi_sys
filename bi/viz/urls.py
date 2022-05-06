from django.urls import path
from django.shortcuts import redirect
from . import views
import importlib
import os
from os import listdir


#### REGISTER URLs
urlpatterns = [
    path('dashboard/<slug:slug>/', views.render_dash),
    path('chart/<slug:slug>/', views.render_chart),
    path('dashboard_library/', views.render_dashboard_library, name='dashboard_library'),
    path('', lambda request: redirect('dashboard_library', permanent=False)),
]


### Import dash apps in dashboards files - called but not used
dashboards = [f for f in listdir((os.path.abspath(os.path.dirname(__file__))+'\dashboards').replace('\\', '/')) if f.endswith('.py')]
for d in dashboards:
    d = d[:d.index('.py')]
    module = importlib.import_module('.dashboards.'+d, package=__package__)
    ### Register dashboard slug with names to redirect lickable link
    urlpatterns.append(path('dashboard/' + d + '/', views.render_dash, name=d))