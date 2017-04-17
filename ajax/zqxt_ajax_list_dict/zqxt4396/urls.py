from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'tools.views.index', name='home'),
    url(r'^add/$', 'tools.views.add', name='add'),
    url(r'^ajax_list/$', 'tools.views.ajax_list', name='ajax-list'),
    url(r'^ajax_dict/$', 'tools.views.ajax_dict', name='ajax-dict'),

    url(r'^admin/', include(admin.site.urls)),
)
