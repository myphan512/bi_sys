from django.db import models
import os
from os import listdir
from django.utils.safestring import mark_safe

# Dashboard model
dashboards = [f for f in listdir((os.path.abspath(os.path.dirname(__file__))+'\dashboards').replace('\\', '/')) if f.endswith('.py')]
dash_choices = tuple([(v, v) for v in dashboards])

class Dashboard(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    file = models.CharField(max_length=250, blank=True, null=True, choices=dash_choices)
    description = models.TextField()
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def format_permitted_roles(self):
        permitted_roles = []
        for role in self.role_set.all():
            permitted_roles.append(role)
        return permitted_roles
    format_permitted_roles.short_description = 'Teams with Access'

    def get_slug(self):
        if not self.file:
            return
        else:
            return str(self.file)[:str(self.file).index('.py')]


# Team Role model
class Role(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    dashboards = models.ManyToManyField(Dashboard,
                                        blank=True, null=True,
                                        verbose_name='Dashboards with Access')

    def __str__(self):
        return self.name

    def format_permitted_dash(self):
        permitted_dash = []
        for dash in self.dashboards.all():
            permitted_dash.append(dash.name)
        return permitted_dash
    format_permitted_dash.short_description = 'Dashboards with Access'

    def image_tag(self):
        return mark_safe('<center>Location: {0}<center>\n<img src="{1}" width="150" height="150" />'.format('static/dashboards/images/logo.png',
                                                                                                                'static/dashboards/images/logo.png'))  # width="150" height="150"
            # return mark_safe('<img src="%s" width="150" height="150" />'.format(self.photo.path))



# Chart model
charts = [f for f in listdir((os.path.abspath(os.path.dirname(__file__))+'\charts').replace('\\', '/')) if f.endswith('.py')]
chart_choices = tuple([(v,v) for v in charts])

class Chart(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200)
    file = models.CharField(max_length=250, blank=True, null=True, choices=chart_choices)

    def __str__(self):
        return self.name

    def get_slug(self):
        if not self.file:
            return
        else:
            return str(self.file)[:str(self.file).index('.py')]
