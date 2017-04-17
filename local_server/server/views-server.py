#coding=utf-8

import os
import sys
import socket
import datetime

from django.shortcuts import render,get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect

from blog.models import Essay,EssayType,Archive,Comment
import config_web as cfg_w

console_path = cfg_w.CONSOLE_WORK_PATH
if console_path not in sys.path:
	sys.path.append(console_path)

import config as cfg
from ecall import *
from verControl import *
from taskinfo import *

import json

g_users = {}
g_groups = {}
g_chosen_user = {}
g_chosen_group = {}
g_login_user = {}

class User(object):
	def __init__(self, name = 'tmp', email = 'tmp', permisson = 'all'):
		self.name = name
		self.email = email
		self.permisson = permisson

	def __dict__(self):
		return {
			'name': self.name,
			'email': self.email,
			'permisson': self.permisson
		}

class Group(object):
	def __init__(self, name = 'tmp', permisson = 'all'):
		self.name = name
		self.permisson = permisson

	def __dict__(self):
		return {
			'name': self.name,
			'permisson': self.permisson
		}

def init_globals():
	global g_users, g_groups, g_login_user
	Trump = User('Trump', 'Trump@gmail.com')
	Clinton = User('Clinton', 'Clinton@gmail.com')
	Obama = User('Obama', 'Obama@gmail.com')
	Bush = User('Bush', 'Bush@gmail.com')
	g_users = [Trump, Clinton, Obama, Bush]
	g_chosen_user = Trump

	communist_party = Group('共产党')
	democratic_party = Group('民主党')
	republican_party = Group('共和党')
	g_groups = [communist_party, democratic_party, republican_party]
	g_chosen_group = republican_party

	g_login_user = User('SHFE.SFIT', 'SHFE.SFIT@hotmail.com')

init_globals()

@csrf_protect
###执行即时任务
def task_rpc(request):
	#if request.method == 'POST':
	if request.method != '':

		#从POST请求中获取查询关键字
		rsp = ''
		#cmdline=request.POST.get('keyword',None)
		cmdline = '--cmd info'
		cmd = 'info'
		print('web req cmd :%s'%(cmdline))

		#if cmdline.find(cfg.SEMICOLON) != -1:
		#	task_type, cmdline = cmdline.split(cfg.SEMICOLON)  ##命令行中有分号
		#else:
		#	task_type = cfg.TASK_TYPE_ECALL
		task_type = cfg.TASK_TYPE_ECALL
		task_info = TaskInfo(state=cfg.FLAG_TASK_READY, TID=0, PID=int(cfg.PID), exec_time=0, \
			cmd=cmd.strip(), cmdline=cmdline.strip(), task_type=int(task_type))
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genRpcHead() + task_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return HttpResponse(rsp.replace("\n", "<br/>"))
	else:
		return index(request)

###执行计划任务
@csrf_protect
def task_ntf(request):
	#if request.method == 'POST':
	if request.method != '':

		#从POST请求中获取查询关键字
		rsp = ''
		#cmdline=request.POST.get('keyword',None)
		cmdline = '--cmd info'
		cmd = 'info'
		tasktime = int(time.time()) + 1800

		print('web req cmd :%s'%(cmdline))
		if cmdline.find(cfg.SEMICOLON) != -1:
			task_type, cmdline = cmdline.split(cfg.SEMICOLON)  ##命令行中有分号
		else:
			task_type = cfg.TASK_TYPE_ECALL
		task_info = TaskInfo(state=cfg.FLAG_TASK_READY, TID=0, PID=int(cfg.PID), exec_time=tasktime, \
			cmd=cmd.strip(), cmdline=cmdline.strip(), task_type=int(task_type))
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genNtfHead() + task_info.encode() + cfg.TIP_INFO_EOF)
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print((traceback.format_exc()))
		return HttpResponse(task_info.encode())
	else:
		return index(request)

###查询计划任务状态
@csrf_protect
def query_all_srvstatus(request):
	#if request.method == 'POST':
	if request.method != '':
		#从POST请求中获取查询关键字
		###
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_SRVSTATUS)
		rsp = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			sock.close()
			rsp_list = rsp.split("\n")
			SrvStatus_list = []
			for token in rsp_list:
				if token.startswith(cfg.TIP_BODY_REQ):
					info = token[len(cfg.TIP_BODY_REQ):]
					srv_status = SrvStatus()
					srv_status.decode(info)
					SrvStatus_list.append(srv_status)
			for info in SrvStatus_list:
				print(info.encode())

		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return HttpResponse(rsp.replace("\n", "<br/>"))
	else:
		return index(request)

###查询计划任务列表
@csrf_protect
def query_all_tasklist(request):
	#if request.method == 'POST':
	if request.method != '':

		#从POST请求中获取查询关键字
		###
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKLIST)
		rsp = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			rsp_list = rsp.split("\n")
			task_list = []
			for token in rsp_list:
				if token.startswith(cfg.TIP_INFO_TASK):
					info = token[len(cfg.TIP_INFO_TASK):]
					task_info = TaskInfo()
					task_info.decode(info)
					task_list.append(task_info)
			for info in task_list:
				print(info.encode())
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return HttpResponse(rsp.replace("\n", "<br/>"))
	else:
		return index(request)

###查询计划任务列表结果
@csrf_protect
def query_all_taskresult(request):
	#if request.method == 'POST':
	if request.method != '':
		#从POST请求中获取查询关键字
		###
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKRESULT)
		rsp = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return HttpResponse(rsp.replace("\n", "<br/>"))
	else:
		return index(request)

###查询版本信息
def query_all_version(request):
	#if request.method == 'POST':
	if request.method != '':

		#从POST请求中获取查询关键字
		###
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_VERSION)
		rsp = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			print 'All Version Rsp: '
			print rsp
			print 'End!'
			sock.close()
			rsp_list = rsp.split("\n")
			version_list = []
			for token in rsp_list:
				if token.startswith(cfg.TIP_BODY_VERINFO):
					info = token[len(cfg.TIP_BODY_VERINFO):]
					version_info = VersionInfo()
					version_info.decode(info)
					version_list.append(version_info)
			for info in version_list:
				print(info.version)
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return HttpResponse(rsp.replace("\n", "<br/>"))
	else:
		return index(request)

def test_task_rpc(request):
	#if request.method == 'POST':
	if request.method != '':

		#从POST请求中获取查询关键字
		rsp = ''
		#cmdline=request.POST.get('keyword',None)
		cmdline = '--cmd info'
		cmd = 'info'
		print('web req cmd :%s'%(cmdline))

		#if cmdline.find(cfg.SEMICOLON) != -1:
		#	task_type, cmdline = cmdline.split(cfg.SEMICOLON)  ##命令行中有分号
		#else:
		#	task_type = cfg.TASK_TYPE_ECALL
		task_type = cfg.TASK_TYPE_ECALL
		task_info = TaskInfo(state=cfg.FLAG_TASK_READY, TID=0, PID=int(cfg.PID), exec_time=0, \
			cmd=cmd.strip(), cmdline=cmdline.strip(), task_type=int(task_type))
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genRpcHead() + task_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			sock.close()
			rsp_data = rsp
			print rsp_data
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		# return HttpResponse(rsp.replace("\n", "<br/>"))
		rsp_data = {'data': 'test_task_rpc!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response
	else:
		return index(request)

def test_task_ntf(request):
	if request.method != '':
		#从POST请求中获取查询关键字
		rsp = ''
		#cmdline=request.POST.get('keyword',None)
		cmdline = '--cmd info'
		cmd = 'info'
		tasktime = int(time.time()) + 1800

		print('web req cmd :%s'%(cmdline))
		if cmdline.find(cfg.SEMICOLON) != -1:
			task_type, cmdline = cmdline.split(cfg.SEMICOLON)  ##命令行中有分号
		else:
			task_type = cfg.TASK_TYPE_ECALL
			task_info = TaskInfo(state=cfg.FLAG_TASK_READY, TID=0, PID=int(cfg.PID), exec_time=tasktime, \
								 cmd=cmd.strip(), cmdline=cmdline.strip(), task_type=int(task_type))
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genNtfHead() + task_info.encode() + cfg.TIP_INFO_EOF)
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print((traceback.format_exc()))
		# return HttpResponse(task_info.encode())

		rsp_data = task_info.__dict__
		# rsp_data = {'data': 'test_task_rpc!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response
	else:
		return index(request)

def test_all_srvstatus(request):
	if request.method != '':
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_SRVSTATUS)
		rsp = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			print 'Test_all_srvstatus'
			print rsp
			sock.close()
			rsp_list = rsp.split("\n")
			SrvStatus_list = []
			for token in rsp_list:
				if token.startswith(cfg.TIP_BODY_REQ):
					info = token[len(cfg.TIP_BODY_REQ):]
					srv_status = SrvStatus()
					srv_status.decode(info)
					SrvStatus_list.append(srv_status.__dict__)
			# for info in SrvStatus_list:
			# 	print(info.encode())
			rsp_data = SrvStatus_list
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		# return HttpResponse(json.dumps(rsp_data), content_type = "application/json")
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response
	else:
		return index(request)

def test_all_tasklist(request):
	#if request.method == 'POST':
	if request.method != '':

		#从POST请求中获取查询关键字
		###
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKLIST)
		rsp_data = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			print rsp
			rsp_list = rsp.split("\n")
			task_list = []
			for token in rsp_list:
				if token.startswith(cfg.TIP_INFO_TASK):
					info = token[len(cfg.TIP_INFO_TASK):]
					task_info = TaskInfo()
					task_info.decode(info)
					task_list.append(task_info.__dict__)
			# for info in task_list:
			# 	print(info.encode())
			sock.close()
			rsp_data = task_list
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		# return HttpResponse(json.dumps(rsp_data), content_type = "application/json")
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response
	else:
		return index(request)

def test_all_taskresult(request):
	if request.method != '':
		print 'test_all_taskresult!'
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKRESULT)
		task_result = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			task_result = recv_end(sock)
			task_result.split('\n')
			print task_result
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return HttpResponse(task_result)
	else:
		return index(request)

def test_all_version(request):
	if request.method != '':
		print '\n+++++ Test_all_version START! +++++'
		print request
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_VERSION)
		rsp = ''
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			tcp_send_head = genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF

			print 'sock send info: '
			print tcp_send_head + '\n'

			rsp = recv_end(sock)
			sock.close()
			rsp_list = rsp.split("\n")
			version_list = []

			for token in rsp_list:
				if token.startswith(cfg.TIP_BODY_VERINFO):
					info = token[len(cfg.TIP_BODY_VERINFO):]
					version_info = VersionInfo()
					version_info.decode(info)
					version_list.append(version_info.__dict__)
			# if info in version_list:
			# 	print info
			rsp_data = version_list
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())

		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response
	else:
		return index(request)

def is_ajax_request(path):
	path_array = path.split('/')
	ajax_flag = 'AJAX'
	if ajax_flag in path_array:
		return True
	else:
		return False

def is_static_file(file_name):
	name_array = file_name.split('/')
	static_flag = 'static'
	if static_flag in name_array:
		return True
	else:
		return False

def delete_headend_slash(strvalue):
	str_start_index = 0
	str_end_index = len(strvalue)
	if strvalue[str_start_index] == '/':
		str_start_index = 1
	if strvalue[str_end_index-1] == '/':
		str_end_index -= 1
	return strvalue[str_start_index:str_end_index]

def get_static_file_name(origin_file_name):
	name_array = origin_file_name.split('/')
	index = 0
	static_flag = 'static'
	for value in name_array:
		if value == static_flag:
			break
		index += 1
	trans_file_name = '/'.join(name_array[index:])
	return delete_headend_slash(trans_file_name)

def get_html_file_name(path):
	name_array = path.split('/')
	return name_array[len(name_array)-1]

def is_empty_html_request(file_name):
	name_array = file_name.split('/')
	last_file_name = name_array[len(name_array)-1]
	if last_file_name.find('.') == -1:
		return True
	else:
		return False

def is_html_request(path_name):
	html_flag = '.html'
	flag = False
	if len(path_name) > len(html_flag) and path_name[-len(html_flag):] == html_flag:
		flag = True
	return flag

def get_file_name(path):
	file_name = delete_headend_slash(path)
	html_flag = '.html'
	# if is_static_file(file_name):
	# 	file_name = get_static_file_name(file_name)
	if is_empty_html_request(file_name):
		file_name += html_flag
	return file_name

def get_ajax_request_name(path):
	name_array = path.split('/')
	ajax_flag = 'AJAX'
	index = 0
	for value in name_array:
		if value == ajax_flag:
			break
		index += 1
	ajax_request_name = '/'.join(name_array[index+1:])
	return delete_headend_slash(ajax_request_name)

def get_ajax_func(path):
	ajax_name = get_ajax_request_name(path)
	print 'ajax_name: ' + ajax_name
	ajax_func_dict = {
		'Request_All_SrvStatus': test_all_srvstatus,
		'Request_All_TaskList': test_all_tasklist,
		'Request_All_TaskResult': test_all_taskresult,
		'Request_All_Version': test_all_version
	}
	ajax_func = ajax_func_dict.get(ajax_name, default_ajax_request)
	return ajax_func

def get_file_object(file_name):
	file_object_dict = {
		'test_req.html': get_test_req_object,
		'admin.html': get_admin_object,
		'admin/auth.html': get_admin_auth_object,
		'admin/logout.html': get_admin_logout_object,
		'admin/password_change.html': get_admin_password_change_object,
		'admin/auth/group.html': get_admin_auth_group_object,
		'admin/auth/group/add.html': get_admin_auth_group_add_object,
		'admin/auth/group/change.html': get_admin_auth_group_change_object,
		'admin/auth/user.html': get_admin_auth_user_object,
		'admin/auth/user/add.html': get_admin_auth_user_add_object,
		'admin/auth/user/change.html': get_admin_auth_user_change_object,
	}
	object_func = file_object_dict.get(file_name, lambda :{})
	print object_func()
	return object_func()

def main_query_rsp(request):
	if is_ajax_request(request.path):
		print '\nIs AJAX Request'
		ajax_func = get_ajax_func(request.path)
		return ajax_func(request)
	else:
		print '\nIs not AJAX Request'
		file_name = get_file_name(request.path)
		file_object = {}
		if is_html_request(file_name):
			file_object = get_file_object(file_name)
		print 'file name: ' + file_name + '\n'
		return render(request, file_name, file_object)

def default_ajax_request(request):
	return HttpResponse(json.dumps({'data':'AJAX Request Failed!'}), content_type = "application/json")

def get_test_req_object():
	user = {
		'name': 'Python'
	}
	users = ['lee', 'Tom', 'Trump', 'Clinton']
	req_object = {
		'name': 'Django',
		'user': user,
		'users': users
	}
	return req_object

def get_admin_object():
	tmp_object = {
		'user': g_login_user
	}
	return tmp_object

def get_admin_auth_object():
	tmp_object = {
		'user': g_login_user
	}
	return tmp_object

def get_admin_logout_object():
	tmp_object = {
		'user': g_login_user
	}
	return tmp_object

def get_admin_password_change_object():
	tmp_object = {
		'user': g_login_user
	}
	return tmp_object

def get_admin_auth_group_object():
	tmp_object = {
		'user': g_login_user,
		'groups': g_groups,
		'group_numbs': len(g_groups)
	}
	return tmp_object

def get_admin_auth_group_add_object():
	tmp_object = {
		'user': g_login_user
	}
	return tmp_object

def get_admin_auth_group_change_object():

	tmp_object = {
		'user': g_login_user,
		'group': g_chosen_group
	}
	return tmp_object

def get_admin_auth_user_object():
	tmp_object = {
		'user': g_login_user,
		'users': g_users,
		'user_numb': len(g_users)
	}
	return tmp_object

def get_admin_auth_user_add_object():
	tmp_object = {
		'user': g_login_user
	}
	return tmp_object

def get_admin_auth_user_change_object():
	tmp_object = {
		'user': g_login_user
	}
	return tmp_object
