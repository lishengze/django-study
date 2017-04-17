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
from django.views.decorators.csrf import csrf_exempt

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

reload(sys)
sys.setdefaultencoding('utf8')

g_users = {}
g_groups = {}
g_chosen_user = {}
g_chosen_group = {}
g_login_user = {}
g_env_array = []
g_get_html_object = {}

# ENV_KEY = 'PTEST_170'
ENV_KEY = 'TEST_170'

class User(object):
	def __init__(self, name = 'tmp', email = 'tmp', permisson = 'all'):
		self.name = name
		self.email = email
		self.permisson = permisson
		self.__dict__ = {
			'name': self.name,
			'email': self.email,
			'permisson': self.permisson
		}

class Group(object):
	def __init__(self, name = 'tmp', permisson = 'all'):
		self.name = name
		self.permisson = permisson
		self.__dict__ = {
			'name': self.name,
			'permisson': self.permisson
		}

class RpcResult(object):
	def __init__(self, data_type, data_array):
		if data_type == 'default':
			self.__dict__ = {
				'object_info': data_array[0],
				'ip_address': data_array[1],
				'cmd_line': ' '.join(data_array[2:])
			}
		if data_type == 'relay':
			self.__dict__ = {
				'origin_ip_address': data_array[0],
				'relay_relation': data_array[1],
			}
		if data_type == 'host':
			self.__dict__ = {
				'ip_address': data_array[0],
				'os_type': data_array[1],
				'host_name': data_array[2]
			}
		if is_version_control_req(data_type):
			self.__dict__ = {
				'SEQ': data_array[0],
				'version': data_array[1],
				'datetime': data_array[2],
				'status': data_array[3]
			}

def init_globals():
	global g_users, g_groups, g_login_user, g_env_array, g_get_html_object
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

	for value in cfg_w.ENV_DICT:
		g_env_array.append(value)
	print 'g_env_array: '
	print g_env_array

init_globals()

def sock_conn(key):
	daemaon_ip = cfg_w.ENV_DICT[key][1]
	daemon_port = cfg_w.ENV_DICT[key][2]
	print(daemaon_ip, daemon_port)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((daemaon_ip, daemon_port))
	return sock

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
			# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			# sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			sock = sock_conn(ENV_KEY)
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

### rpc 请求相关代码
def process_rpc_result(origin_data, data_type):
	failed_data = get_rpc_failed_data(origin_data, data_type)
	if failed_data == '':
		array_data = []
		if is_version_control_req(data_type):
			array_data = get_version_ctr_array_result(origin_data)
		else:
			array_data = get_task_rpc_array_result(origin_data)
		print array_data
		dict_data = get_rpc_dict_result(array_data, data_type)
		return {'data': dict_data, 'type': data_type}
	else:
		return {'data': failed_data, 'type': 'Failed'}

def get_rpc_failed_data(origin_data, data_type):
	tmpdata = origin_data.split('\n')
	failed_data = tmpdata
	if is_version_control_req(data_type):
		for value in tmpdata:
			if value.find('---') != -1:
				failed_data = ''
				break
	else:
		failed_data = ''
	return failed_data

def is_version_control_req(data_type):
	if data_type.find('version_control') != -1:
		return True
	else:
		return False

def get_version_ctr_array_result(origin_data):
	tmpdata = origin_data.split('\n')
	array_data = []
	tmpdata = tmpdata[len(tmpdata)-2].split('\t')
	array_data.append(tmpdata)
	# print tmpdata
	# for value in tmpdata:
	# 	if value != '':
	# 		array_data.append(value)
	return array_data

def get_task_rpc_array_result(origin_data):
	tmpdata = origin_data.split('\n')
	tmpdata = tmpdata[1:len(tmpdata)-1]
	index = 0
	str_head = '[info]xxx: '
	final_result = []
	while index < len(tmpdata):
		tmp_result = []
		tmpdata[index] = tmpdata[index][len(str_head):]
		tmpdata[index] = tmpdata[index].split(' ')
		# print tmpdata[index]
		for value in tmpdata[index]:
			if value != '':
				tmp_result.append(value)
		final_result.append(tmp_result)
		index += 1
	return final_result

def get_rpc_dict_result(array_data, data_type):
	index = 0
	dict_data = []
	while index < len(array_data):
		tmp_dict_data = RpcResult(data_type, array_data[index])
		dict_data.append(tmp_dict_data.__dict__)
		index += 1
	return dict_data

### 请求相关.
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
		'Set_ENV_KEY': g_ajax_func.set_env_key,
		'Request_All_SrvStatus': g_ajax_func.test_all_srvstatus,
		'Request_All_TaskList': g_ajax_func.test_all_tasklist,
		'Request_All_TaskResult': g_ajax_func.test_all_taskresult,
		'Request_All_Version': g_ajax_func.test_all_version,
        'Request_Task_Rpc': g_ajax_func.test_task_rpc,
        'Request_Task_Ntf': g_ajax_func.test_task_ntf,
		'Set_Chosen_GroupOrUser': g_ajax_func.set_chosen_grouporuser,
		'Upload_File': g_ajax_func.upload_file,

	}
	ajax_func = ajax_func_dict.get(ajax_name, g_ajax_func.default_ajax_request)
	return ajax_func

def get_file_object(file_name):
	file_object_dict = {
		'test_req.html': g_get_html_object.get_test_req_object,
		'login.html': g_get_html_object.get_login_object,
		'admin.html': g_get_html_object.get_admin_object,
		'admin/auth.html': g_get_html_object.get_admin_auth_object,
		'admin/logout.html': g_get_html_object.get_admin_logout_object,
		'admin/password_change.html': g_get_html_object.get_admin_password_change_object,
		'admin/auth/group.html': g_get_html_object.get_admin_auth_group_object,
		'admin/auth/group/add.html': g_get_html_object.get_admin_auth_group_add_object,
		'admin/auth/group/change.html': g_get_html_object.get_admin_auth_group_change_object,
		'admin/auth/user.html': g_get_html_object.get_admin_auth_user_object,
		'admin/auth/user/add.html': g_get_html_object.get_admin_auth_user_add_object,
		'admin/auth/user/change.html': g_get_html_object.get_admin_auth_user_change_object,
	}
	object_func = file_object_dict.get(file_name, lambda :{})
	print object_func()
	return object_func()

@csrf_exempt
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



def uploadFile(sock, FileSrc, FileDst):
	try:
		file_md5 = md5sum(FileSrc)
		filename = os.path.basename(FileSrc)
		f = open(FileSrc, 'rb')
		sock.send(genFileHead(filename, file_md5, FileDst))
		bytes = 0
		while 1:
			fileinfo = f.read(cfg.DEFAULT_RECV)
			if not fileinfo:
				break
			bytes = bytes + len(fileinfo)
			#print('Send ' + str(bytes) + ' bytes ...')
			sock.send(fileinfo)
			#time.sleep(0.001)
		sock.send(cfg.TIP_INFO_EOF)
		rtn = cfg.CMD_SUCC
	except Exception as e:
		rtn = cfg.CMD_FAIL
		print(traceback.format_exc())
	finally:
		return rtn

def downloadFile(sock, FileSrc, FileDst):
	try:
		sock.send(genFReqHead(FileSrc) + cfg.TIP_INFO_EOF)
		rsp = recv_end(sock)
		head_info, buf = getFRspHead(rsp)
		print(head_info)
		print('++++++++')
		print(buf)
		seq_id, filename, status = getFRspInfo(head_info.strip())
		print(filename, status)
		if int(status) == cfg.CMD_SUCC:
			## dir exsit?
			f = open(FileDst, 'w')
			f.write(buf)
			f.close()
			rtn = cfg.CMD_SUCC
		else:
			rtn = cfg.CMD_FAIL
	except Exception as e:
		rtn = cfg.CMD_FAIL
		print(traceback.format_exc())
	finally:
		return rtn

@csrf_protect
def upload_file_pro(request):
	rsp = ''
	if request.method == "POST":
		start_time = int(time.time())
		myFile = request.FILES.get("myfile", None)
		if not myFile:
			return HttpResponse("no files for upload!")
		filepath = os.path.join(cfg.WORK_PATH_TEMP, myFile.name)
		filedst = filepath + cfg.DOT + cfg.PID
		destination = open(filepath,'wb+')
		for chunk in myFile.chunks():
			destination.write(chunk)
		destination.close()

		sock = sock_conn(ENV_KEY)
		rtn = uploadFile(sock, filepath, filedst)
		end_time = int(time.time())
		if rtn == cfg.CMD_SUCC:
			rsp = recv_end(sock)
			info = '<br/>File transfer SUCC, cost ' + str(end_time - start_time) + ' secs.'
		else:
			info = '<br/>File transfer FAIL, cost ' + str(end_time - start_time) + ' secs.'
		rsp = rsp + info
		sock.close()
		return HttpResponse(rsp)
	else:
		return index(request)

class AjaxReqFunc(object):
	def __init__ (self):
		self.name = 'AjaxReqFunc'

	def default_ajax_request(self, request):
		return HttpResponse(json.dumps({'data':'AJAX Request Failed!'}), content_type = "application/json")

	def upload_file(self, request):
		rsp_data = {}
		if request.method == 'POST':
			start_time = int(time.time())
			upload_file = request.FILES['file']
			if upload_file:
				filename = str(upload_file).encode('utf-8')
				filepath = os.path.join(cfg.WORK_PATH_TEMP, filename)
				filedst = filepath + cfg.DOT + cfg.PID
				print 'filepath: ', filepath
				print 'filedest: ', filedst

				destination = open(filepath,'wb+')
				for chunk in upload_file.chunks():
					destination.write(chunk)
				destination.close()
				sock = sock_conn(ENV_KEY)
				rtn = uploadFile(sock, filepath, filedst)
				end_time = int(time.time())

				status = ''
				upload_time = str(end_time - start_time)
				print 'rtn: ', rtn
				if rtn == cfg.CMD_SUCC:
					rsp = recv_end(sock)
					info = '<br/>File transfer SUCC, cost ' + str(end_time - start_time) + ' secs.'
					status = "Successful"
				else:
					info = '<br/>File transfer FAIL, cost ' + str(end_time - start_time) + ' secs.'
					status = 'Failed'
				rsp = rsp + info
				print rsp
				print 'status: ', status
				sock.close()
				rsp_data = {
					'type': status,
					'upload_time': upload_time
				}
			else:
				rsp_data = {
					'type': 'Failed',
					'info': 'No upload file'
				}
		else:
			rsp_data = {
				'type': 'Failed',
				'info': 'Is Not POST Requset!'
			}
		return HttpResponse(json.dumps(rsp_data), content_type = "application/json")

	def handle_uploaded_file(self, file, filename):
		filename = filename.encode('utf-8')
		print 'filename: ', filename
		if not os.path.exists('upload/'):
			os.mkdir('upload/')
		full_file_name = 'upload/' + filename
		print 'full_file_name: ', full_file_name
		with open(full_file_name, 'wb+') as destination:
			for chunk in file.chunks():
				destination.write(chunk)
		destination.close()
		return full_file_name


	def set_env_key(self, request):
		global ENV_KEY
		print 'This is AjaxReqFunc.set_env_key!'
		req_env_key_value = request.POST.getlist('env_key_value')[0]

		ENV_KEY = req_env_key_value
		print 'ENV_KEY: ', ENV_KEY

		rsp_data = {
			'data': req_env_key_value
		}
		response = HttpResponse(json.dumps(rsp_data))
		# response = HttpResponse(req_json)
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	@csrf_exempt
	def test_task_rpc(self, request):
		if request.method != '':
			req_json = request.POST.getlist('req_json')[0]
			print req_json
			trans_req_json = json.loads(req_json)
			print trans_req_json

			task_type = cfg.TASK_TYPE_ECALL
			cmdline = ''
			if 'type' in trans_req_json and trans_req_json['type'] == 'version_control':
				data_type = 'version_control_' + trans_req_json['--cmd']
				task_type = cfg.TASK_TYPE_VERCONTROL
			elif '--args' not in trans_req_json or trans_req_json['--args'] == '' or \
				trans_req_json['--args'] =='app':
				data_type = 'default'
			else:
				data_type = trans_req_json['--args']

			print 'data_type: ', data_type
			print 'task_type: ', task_type
			req_para = ['--cmd', '--args', '--grp', \
						'--ctr', '--srv', '--srvno',\
						'--ictr', '--isrv', '--isrvno']
			for value in req_para:
				if value in req_para and value in trans_req_json and trans_req_json[value] !='':
					cmdline += value + ' ' + trans_req_json[value] + ' '
			print ('\nThe REQUEST command line is: %s\n' %(cmdline))

			original_rsp_data = ''
			cmd = 'info'

			task_info = TaskInfo(state=cfg.FLAG_TASK_READY, TID=0, PID=int(cfg.PID), exec_time=0, \
						cmd=cmd.strip(), cmdline=cmdline.strip(), task_type=int(task_type))
			trans_rsp_data = {}
			try:
				# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				# sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
				sock = sock_conn(ENV_KEY)
				sock.send(genRpcHead() + task_info.encode() + cfg.TIP_INFO_EOF)
				original_rsp_data = recv_end(sock)
				sock.close()
				print ('The original rsp data is:\n%s' %(original_rsp_data))
				trans_rsp_data = process_rpc_result(original_rsp_data, data_type)
				print 'Transed Rsp Data: '
				print trans_rsp_data
			except Exception as e:
				print('notifyDaemon failed!')
				print(traceback.format_exc())
			rsp_data = trans_rsp_data
			response = HttpResponse(json.dumps(rsp_data))
			# response = HttpResponse(req_json)
			response["Access-Control-Allow-Origin"] = "*"
			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
			response["Access-Control-Max-Age"] = "1000"
			response["Access-Control-Allow-Headers"] = "*"
			return response
		else:
			return index(request)

	def test_task_ntf(self, request):
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
				# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				# sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
				sock = sock_conn(ENV_KEY)
				sock.send(genNtfHead() + task_info.encode() + cfg.TIP_INFO_EOF)
				rsp = recv_end(sock)
				print rsp
				sock.close()
			except Exception as e:
				print('notifyDaemon failed!')
				print((traceback.format_exc()))
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

	def test_all_srvstatus(self, request):
		if request.method != '':
			req_info = ReqInfo(0, cfg.FLAG_REQTYPE_SRVSTATUS)
			rsp = ''
			try:
				# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				# sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
				sock = sock_conn(ENV_KEY)
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

	def test_all_tasklist(self, request):
		#if request.method == 'POST':
		if request.method != '':

			#从POST请求中获取查询关键字
			###
			req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKLIST)
			rsp_data = ''
			try:
				# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				# sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
				sock = sock_conn(ENV_KEY)
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

	def test_all_taskresult(self, request):
		if request.method != '':
			print 'test_all_taskresult!'
			req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKRESULT)
			task_result = ''
			try:
				# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				# sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
				sock = sock_conn(ENV_KEY)
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

	def test_all_version(self, request):
		if request.method != '':
			print '\n+++++ Test_all_version START! +++++'
			print request
			req_info = ReqInfo(0, cfg.FLAG_REQTYPE_VERSION)
			rsp = ''
			rsp_data = ''
			try:
				# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				# sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
				sock = sock_conn(ENV_KEY)
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

	def set_chosen_grouporuser(self, request):
		global g_users, g_groups, g_chosen_user, g_chosen_group
		test_value = request.POST.getlist('test_value')[0]
		# print test_value
		test_value = test_value.encode('utf-8')
		print test_value
		rsp_url = ''
		error_info = ''

		is_user_request = False
		is_group_request = False
		for group in g_groups:
			if test_value == group.name:
				g_chosen_group = group
				is_group_request = True
		for user in g_users:
			if test_value == user.name:
				g_chosen_user = user
				is_user_request = True

		if is_group_request:
			rsp_url = '/admin/auth/group/change'
		elif is_user_request:
			rsp_url = '/admin/auth/user/change'
		else :
			error_info = 'request name does not exit!'

		rsp_data = {'data': rsp_url,
					'error': error_info}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

class GetHtmlObject(object):
	def __init__(self):
		self.name = 'GetHtmlObject'

	def get_test_req_object(self):
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

	def get_login_object(self):
		req_object = {
			'ENV_KEY': g_env_array
		}
		return req_object

	def get_admin_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_auth_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_logout_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_password_change_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_auth_group_object(self):
		tmp_object = {
			'user': g_login_user,
			'groups': g_groups,
			'group_numbs': len(g_groups)
		}
		return tmp_object

	def get_admin_auth_group_add_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_auth_group_change_object(self):
		tmp_object = {
			'login_user': g_login_user,
			'group': g_chosen_group
		}
		return tmp_object

	def get_admin_auth_user_object(self):
		tmp_object = {
			'user': g_login_user,
			'users': g_users,
			'user_numb': len(g_users)
		}
		return tmp_object

	def get_admin_auth_user_add_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_auth_user_change_object(self):
		tmp_object = {
			'login_user': g_login_user,
			'chosen_user': g_chosen_user
		}
		return tmp_object

g_ajax_func = AjaxReqFunc()

g_get_html_object = GetHtmlObject()
