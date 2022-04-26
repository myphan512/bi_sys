from django.urls import path
from django.shortcuts import redirect
from . import views
import importlib
import os
from os import listdir

### Import python files in dashboards folder
dashboards = [f for f in listdir((os.path.abspath(os.path.dirname(__file__))+'\dashboards').replace('\\', '/')) if f.endswith('.py')]
for d in dashboards:
    d = d[:d.index('.py')]
    module = importlib.import_module('.dashboards.'+d, package=__package__)

#### REGISTER URLs
urlpatterns = [
    path('dashboard/<slug:slug>/', views.render_dash),
    path('', views.render_dashboard_library, name='dashboard_library'),
    path('chart/<slug:slug>/', views.render_chart),
    path('dashboard_library', lambda request: redirect('dashboard_library', permanent=False)),
]