from django.http import HttpResponse, Http404
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
import json

def index (request) :
	templateName = 'index.html'
	return render(request, templateName)

def get_jquery (request):
	return render(request, 'src/jquery-1.8.3/jquery.min.js')

def get_highchart (request):
	return render(request, "src/Highcharts-4.2.6/js/highcharts.js")

def get_highstock (request):
	return render(request, "src/Highstock-4.2.6/js/highstock.js")

def get_highchart_data (request):
	return render(request, "src/Highcharts-4.2.6/js/data.js")

def get_highchart_drilldown (request):
	return render(request, "src/Highcharts-4.2.6/js/drilldown.js")

def get_chart (request):
	return render(request, "chart-origin.js")

@csrf_exempt
def sendData (request):
	a1 = request.POST['ss']
	a3 = request.POST.getlist('ss')
	a2 = request.POST['st']
	data = {'A': a3, 'B': a2}
	return HttpResponse(json.dumps(data), content_type= "application/json")	

def ajax_dict (request):
    tmpObj = Student()
	return HttpResponse(json.dumps(tmpObj), content_type = "application/json")

# class Main(object):
# 	def __init__(self):
# 		self.name = 'main'
	
# 	def m_ajax_dict(self, request):
# 		name_dict = {'twz': 'Life is short! Go on!'}
# 		return HttpResponse(json.dumps(name_dict), content_type = "application/json")

# main_site = Main()

# class AdminSite(object):
# 	def __init__(self):
# 		self.name = 'admin_size'

# 	def urls(self, request):
# 		url_path = request.path
# 		url_array = url_path.split('/')
# 		template_name = url_path[1:len(url_path)-1] + '.html'
# 		return render(request, template_name)

# 	def query_static(self, request):
#     		path_name = request.path
# 			# path_array = path_name.split('/')
# 			# static_index = 0
# 			# for value in path_array:
#     		# 		if 'static' == value:
#     		# 				break
# 			# 		static_index += 1
# 			# static_file_name = '/'.join(path_array[static_index:])
# 			# return render(request, static_file_name)


# admin_site = AdminSite()