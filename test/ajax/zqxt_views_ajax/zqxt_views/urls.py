from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'calc.views.index', name='index'),
    url(r'^add/((?:-|\d)+)/((?:-|\d)+)/$', 'calc.views.add', name='add'),

    url(r'^admin/', include(admin.site.urls)),
)
