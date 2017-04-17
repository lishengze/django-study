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
from blog import views as blog_views

import config_web as cfg_w

admin.autodiscover() 
urlpatterns = [
    url(r'^admin/', admin.site.urls),
   url(r'root/(?P<path>.*)$', serve,
   {'document_root': cfg_w.TEMPLATES_PATH}),
    url(r'^account/login/', blog_views.alogin),
   	url(r'^account/register/', blog_views.register),
    url(r'^account/logout/', blog_views.alogout), 
#    url(r'^essay/(?P<eid>\d+)/$',blog_views.essay_details),
 #   url(r'^search/$',blog_views.task),
 	###执行即时任务
 	url(r'^task1/$',blog_views.task_rpc),
 	###执行计划任务
 	url(r'^task2/$',blog_views.task_ntf),
 	#url(r'^task3/$',blog_views.file_upload),
 	url(r'^uploadFile/$',blog_views.upload_file),
 	url(r'^downloadFile/$',blog_views.download_file),
    url(r'^req1/$',blog_views.query_all_srvstatus),
    url(r'^req2/$',blog_views.query_all_tasklist),
    url(r'^req3/$',blog_views.query_all_taskresult),
    url(r'^req4/$',blog_views.query_all_version),
    url(r'^leavemsg/(?P<eid>\d+)/$',blog_views.leave_comment1),
    url(r'^(?P<pageNo>\d+)/(?P<etype>\d+)/$',blog_views.index),
    url(r'^latest/feed/$', LatestEntriesFeed()),
    url(r'^',blog_views.index),
]
