from django.urls import path
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
    path('<slug:slug>/', views.render_dash)
]