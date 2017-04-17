"""highchart URL Configuration

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
from app.view import index, get_jquery, get_highchart, get_highchart_data, get_highchart_drilldown, get_chart
from app.view import sendData, ajax_dict

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/$', index),
    url(r'jquery.min.js/$', get_jquery),
    url(r'highcharts.js/$', get_highchart),
    url(r'data.js/$', get_highchart_data),
    url(r'drilldown.js/$', get_highchart_drilldown),
    url(r'^chart.js/$', get_chart),
    url(r'^sendData/$', sendData),
    url(r'ajax_dict', ajax_dict), 
]
