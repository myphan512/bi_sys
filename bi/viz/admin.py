from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe
from .models import Dashboard, Role, Chart
from .views import *

# Role Admin Site
class RoleAdmin(admin.ModelAdmin):
    filter_horizontal = ['dashboards']
    list_display = ['id', 'name', 'format_permitted_dash', ]
    ordering = ['id']
    readonly_fields = ['image_tag']

# Chart Admin Site
class ChartAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'chart_url']
    ordering = ['id']

    def chart_url(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(reverse(render_chart, args=[obj.get_slug()]), obj.get_slug()))
    chart_url.allow_tags = True
    chart_url.short_description = 'slug'

# Chart Dashboard Site
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'dash_url', 'description', 'format_permitted_roles', 'active']
    ordering = ['id']

    def dash_url(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(reverse(render_dash, args=[obj.get_slug()]), obj.get_slug()))
    dash_url.allow_tags = True
    dash_url.short_description = 'slug'

### Register your models here.
admin.site.register(Dashboard, DashboardAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Chart, ChartAdmin)
