#coding=utf-8
"""blog_test URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.static import serve
from feed import LatestEntriesFeed
# from blog import views as blog_views
from blog.views import server_view
from blog import oldView as blog_views
from django.views.generic.base import RedirectView

import config_web as cfg_w

admin.autodiscover()
urlpatterns = [
    # url(r'^admin/', admin.site.urls),


 	#url(r'^task1/$',blog_views.task_rpc),
 	url(r'^task2/$',blog_views.task_ntf),
    url(r'^req1/$',blog_views.query_all_srvstatus),
    url(r'^req2/$',blog_views.query_all_tasklist),
    url(r'^req3/$',blog_views.query_all_taskresult),
    url(r'^req4/$',blog_views.query_all_version),
    url(r'^favicon.ico', RedirectView.as_view(url=r'static/images/favicon.ico')),

    url(r'^', server_view.main_query_rsp),
    # url(r'^', blog_views.main_query_rsp),
    # url(r'^test_req/', blog_views.main_query_rsp),
    # url(r'AJAX/Request_All_SrvStatus/$', blog_views.test_all_srvstatus),
    # url(r'AJAX/Request_All_Version/$', blog_views.test_all_version),
    # url(r'AJAX/Request_All_TaskList/$', blog_views.test_all_tasklist),
    # url(r'AJAX/Request_All_TaskResult/$', blog_views.test_all_taskresult),
    # url(r'root/(?P<path>.*)$', serve,
    # url(r'^account/login/', blog_views.alogin),
    # url(r'^account/register/', blog_views.register),
    # url(r'^account/logout/', blog_views.alogout),
    # url(r'^leavemsg/(?P<eid>\d+)/$',blog_views.leave_comment1),
    # url(r'^(?P<pageNo>\d+)/(?P<etype>\d+)/$',blog_views.index),
    # url(r'^latest/feed/$', LatestEntriesFeed()),
    # {'document_root': cfg_w.TEMPLATES_PATH}),
    # url(r'^',blog_views.index),
]
