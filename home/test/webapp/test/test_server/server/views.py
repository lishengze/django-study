#coding=utf-8

import os
import sys
import socket
import datetime
import time
import threading

from django.shortcuts import render,get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt

import config_web as cfg_w
import types

console_path = cfg_w.CONSOLE_WORK_PATH
if console_path not in sys.path:
	sys.path.append(console_path)

import config as cfg
from ecall import *
from verControl import *
from taskinfo import *

import json

from models import GroupInfo
from models import UserInfo
import shutil

reload(sys)
sys.setdefaultencoding('utf8')

g_users = {}
g_groups = {}
g_chosen_user = {}
g_chosen_group = {}
g_login_user = {}
g_env_array = []
g_get_html_object = {}
g_group_permission = []
g_user_permission = []

# ENV_KEY = 'PTEST_170'
ENV_KEY = 'TEST_170'

class User(object):
	def __init__(self, name = 'tmp', email = 'tmp', permission = 'all', groups = 'all', password = 'tmp'):
		self.name = name
		self.email = email
		self.permission = permission
		self.groups = groups
		self.password = password
		self.__dict__ = {
			'name': self.name,
			'email': self.email,
			'permission': self.permission,
			'groups': self.groups,
			'password': self.password
		}

class Group(object):
	def __init__(self, name = 'tmp', permission = 'all'):
		self.name = name
		self.permission = permission
		self.__dict__ = {
			'name': self.name,
			'permission': self.permission
		}

class RpcResult(object):
	def __init__(self, data_type, data_array):
		if data_type == 'default':
			self.__dict__ = {
				'object_info': data_array[1],
				'ip_address': data_array[0],
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
			# if data_type.find('show')!= -1 or data_type.find('rollback')!= -1 or data_type.find('drop')!= -1:
			# 	# print data_array
			# 	self.__dict__ = {
			# 		'SEQ': data_array[0],
			# 		'version': data_array[1],
			# 		'datetime': data_array[2],
			# 		'status': data_array[3]
			# 	}
			# else:
			# 	self.__dict__ = {
			# 		'info': data_array
			# 	}

def init_globals():
	global g_users, g_groups, g_login_user, \
		   g_env_array, g_get_html_object, \
		   g_group_permission, g_user_permission

	Trump = User('Trump', 'Trump@gmail.com')
	Clinton = User('Clinton', 'Clinton@gmail.com')
	Obama = User('Obama', 'Obama@gmail.com')
	Bush = User('Bush', 'Bush@gmail.com')
	g_users = [Trump, Clinton, Obama, Bush]
	g_chosen_user = Trump

	# communist_party = Group('共产党')
	# democratic_party = Group('民主党')
	# republican_party = Group('共和党')
	communist_party = Group('Communist Party')
	democratic_party = Group('Democratic Party')
	republican_party = Group('Republican Party')
	g_groups = [communist_party, democratic_party, republican_party]

	g_chosen_group = republican_party
	g_login_user = User('SHFE.SFIT', 'SHFE.SFIT@hotmail.com')

	g_group_permission = ["管理用户权限", \
						  "运维管理|信息查询", \
						  "运维管理|安装部署", \
						  "运维管理|进程控制", \
						  "版本控制|查询", \
						  "版本控制|发布", \
						  "版本控制|回退", \
						  "版本控制|删除", \
						  "版本控制|文本差异化比较", \
						  "即时任务|配置管理", \
						  "即时任务|查询状态", \
						  "计划任务|查询状态"]
	g_user_permission = g_group_permission

	for value in cfg_w.ENV_DICT_KEY:
		# print value
		g_env_array.append(value)
	# print 'g_env_array: '
	# print g_env_array

init_globals()

def getKey(key):
	daemaon_ip = cfg_w.ENV_DICT[key][1]
	daemon_port = cfg_w.ENV_DICT[key][2]
	print(key, daemaon_ip, daemon_port)
	return daemaon_ip, daemon_port

def sock_conn(daemaon_ip, daemon_port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((daemaon_ip, daemon_port))
	except Exception:
		print(traceback.format_exc())
		sock = sock_conn(daemaon_ip, daemon_port)
	return sock

def is_version_control_req(data_type):
	if data_type.find('version_control') != -1:
		return True
	else:
		return False

def output_msg(description, info, *other_info):
	print description
	print info
	for value in other_info:
		print value
	print ''

class ViewMain(object):
	def __init__(self):
		self.name = "ViewMain"
		self._ajax_func = AjaxReqFunc()
		self._get_html_object = GetHtmlObject()

	def is_ajax_request(self, path):
		path_array = path.split('/')
		ajax_flag = 'AJAX'
		if ajax_flag in path_array:
			return True
		else:
			return False

	def is_static_file(self, fileName):
		name_array = fileName.split('/')
		static_flag = 'static'
		if static_flag in name_array:
			return True
		else:
			return False

	def delete_headend_slash(self, strvalue):
		str_start_index = 0
		str_end_index = len(strvalue)
		if strvalue[str_start_index] == '/':
			str_start_index = 1
		if strvalue[str_end_index-1] == '/':
			str_end_index -= 1
		return strvalue[str_start_index:str_end_index]

	def get_static_fileName(self, origin_fileName):
		name_array = origin_fileName.split('/')
		index = 0
		static_flag = 'static'
		for value in name_array:
			if value == static_flag:
				break
			index += 1
		trans_fileName = '/'.join(name_array[index:])
		return self.delete_headend_slash(trans_fileName)

	def get_html_fileName(self, path):
		name_array = path.split('/')
		return name_array[len(name_array)-1]

	def is_empty_html_request(self, fileName):
		name_array = fileName.split('/')
		last_fileName = name_array[len(name_array)-1]
		if last_fileName.find('.') == -1:
			return True
		else:
			return False

	def is_html_request(self, path_name):
		html_flag = '.html'
		flag = False
		if len(path_name) > len(html_flag) and path_name[-len(html_flag):] == html_flag:
			flag = True
		return flag

	def get_fileName(self, path):
		fileName = self.delete_headend_slash(path)
		html_flag = '.html'
		# if is_static_file(fileName):
		# 	fileName = get_static_fileName(fileName)
		if self.is_empty_html_request(fileName):
			fileName += html_flag
		return fileName

	def get_html_fileName_and_id(self, fileName):
		html_flag = '.html'
		fileName = fileName[:len(fileName)-len(html_flag)]
		fileName_array = fileName.split('/')
		print fileName_array
		if fileName_array[len(fileName_array)-1] == 'change' and fileName_array[len(fileName_array)-2].isdigit():
			data_id = fileName_array[len(fileName_array)-2]
			fileName_array.remove(fileName_array[len(fileName_array)-2])
			fileName = '/'.join(fileName_array)
			fileName = self.delete_headend_slash(fileName) + html_flag
			return {
				'id': data_id,
				'fileName': fileName,
			}
		elif fileName_array[len(fileName_array)-1].find('search=') != -1:
			data_id = fileName_array[len(fileName_array)-1][len('search='):]
			fileName_array.remove(fileName_array[len(fileName_array)-1])
			fileName = '/'.join(fileName_array)
			fileName = self.delete_headend_slash(fileName) + html_flag
			return {
				'id': data_id,
				'fileName': fileName,
			}
		else:
			return False

	def get_ajax_request_name(self, path):
		name_array = path.split('/')
		ajax_flag = 'AJAX'
		index = 0
		for value in name_array:
			if value == ajax_flag:
				break
			index += 1
		ajax_request_name = '/'.join(name_array[index+1:])
		return self.delete_headend_slash(ajax_request_name)

	def get_ajax_func(self, path):
		ajax_name = self.get_ajax_request_name(path)
		print 'ajax_name: ' + ajax_name
		ajax_func_dict = {
			'Set_ENV_KEY': self._ajax_func.set_env_key,
			'Request_All_SrvStatus': self._ajax_func.test_all_srvstatus,
			'Request_All_TaskList': self._ajax_func.test_all_tasklist,
			'Request_All_TaskResult': self._ajax_func.test_all_taskresult,
			'Request_All_Version': self._ajax_func.test_all_version,
	        'Request_Task_Rpc': self._ajax_func.test_task_rpc,
	        'Request_Task_Ntf': self._ajax_func.request_ntf_task,
			'Request_Real_Time_Info_Task':self._ajax_func.request_real_time_info_task,
			'Request_Real_Time_VersionCtr_Task': self._ajax_func.request_real_time_versionCtr_task,
			'Get_NTF_Task_Result': self._ajax_func.get_all_ntf_task_result,
			'Get_NTF_Task_State': self._ajax_func.get_all_ntf_task_state,
			'Request_User_Login': self._ajax_func.request_user_login,
			'Upload_File': self._ajax_func.upload_file,
			'Update_Srv': self._ajax_func.update_srv,
			'Set_DB_Data': self._ajax_func.set_dbdata,
			'Get_DB_Data': self._ajax_func.get_dbdata,
			'Set_Chosen_Group': self._ajax_func.set_chosen_group,
			'Set_Chosen_User': self._ajax_func.set_chosen_user,
			'Delete_Group': self._ajax_func.delete_group_data,
			'Delete_User': self._ajax_func.delete_user_data,
			'Add_User': self._ajax_func.add_user_data,
			'Add_Group': self._ajax_func.add_group_data,
			'Change_User': self._ajax_func.change_user_data,
			'Change_Group': self._ajax_func.change_group_data,
			'Change_User_Password': self._ajax_func.change_user_password,
		}
		ajax_func = ajax_func_dict.get(ajax_name, self._ajax_func.default_ajax_request)
		return ajax_func

	def get_file_object(self, fileName, id = -1):
		file_object_dict = {
			'test_req.html': self._get_html_object.get_test_req_object,
			'login.html': self._get_html_object.get_login_object,
			'admin.html': self._get_html_object.get_admin_object,
			'admin/auth.html': self._get_html_object.get_admin_auth_object,
			'admin/logout.html': self._get_html_object.get_admin_logout_object,
			'admin/password_change.html': self._get_html_object.get_admin_password_change_object,
			'admin/auth/group.html': self._get_html_object.get_admin_auth_group_object,
			'admin/auth/group/add.html': self._get_html_object.get_admin_auth_group_add_object,
			'admin/auth/group/change.html': self._get_html_object.get_admin_auth_group_change_object,
			'admin/auth/user.html': self._get_html_object.get_admin_auth_user_object,
			'admin/auth/user/add.html': self._get_html_object.get_admin_auth_user_add_object,
			'admin/auth/user/change.html': self._get_html_object.get_admin_auth_user_change_object,
		}
		object_func = file_object_dict.get(fileName, lambda :{})
		if id !=-1:
			# print object_func(id)
			return object_func(id)
		else:
			print object_func()
			return object_func()

	def get_upload_file_env_key(self, filePath):
		ENV_KEY = ''
		exec_time = -1
		# output_msg('filePath', filePath)
		pathArray = filePath.split('/')
		# output_msg('pathArray', pathArray)
		if filePath.find('Upload_File') != -1:
			# ENV_KEY = filePath[(filePath.find('Upload_File') + len('Upload_File') + 1):]
			ENV_KEY = pathArray[len(pathArray)-1]
			filePath = filePath[0:filePath.find('Upload_File') + len('Upload_File') + 1]
			# output_msg('ENV_KEY', ENV_KEY)
			# output_msg('filePath', filePath)
		elif filePath.find('Update_Srv') != -1:
			exec_time = pathArray[len(pathArray)-1]
			ENV_KEY = pathArray[len(pathArray)-2]
			filePath = filePath[0:filePath.find('Update_Srv') + len('Update_Srv') + 1]
		return {
			'ENV_KEY': ENV_KEY,
			'filePath': filePath,
			'exec_time': exec_time
		}

	@csrf_exempt
	def main_query_rsp(self, request):
		if self.is_ajax_request(request.path):
			print '\nIs AJAX Request'
			tmpData = self.get_upload_file_env_key(request.path)
			output_msg('tmpData', tmpData)
			filePath = tmpData['filePath']
			ajax_func = self.get_ajax_func(filePath)

			if tmpData['ENV_KEY'] == '':
				return ajax_func(request)
			elif tmpData['exec_time'] == -1:
				return ajax_func(request, tmpData['ENV_KEY'])
			else:
				return ajax_func(request, tmpData['ENV_KEY'], tmpData['exec_time'])
		else:
			print '\nIs not AJAX Request'
			print 'request.path: ', request.path
			fileName = self.get_fileName(request.path)
			file_object = {}
			if self.is_html_request(fileName):
				return_data = self.get_html_fileName_and_id(fileName)
				print return_data
				if return_data:
					fileName = return_data['fileName']
					file_object = self.get_file_object(fileName, return_data['id'])
				else:
					file_object = self.get_file_object(fileName)
			print 'file name: ' + fileName + '\n'
			return render(request, fileName, file_object)

# class HandleFileAjaxFunc(object):
# 	def __init__(self):
# 		self.name = 'HandleFile'
#
# 	def uploadFile(self, sock, FileSrc, FileDst):
# 		try:
# 			file_md5 = md5sum(FileSrc)
# 			filename = os.path.basename(FileSrc)
# 			f = open(FileSrc, 'rb')
# 			sock.send(genFileHead(filename, file_md5, FileDst))
# 			bytes = 0
# 			while 1:
# 				fileinfo = f.read(cfg.DEFAULT_RECV)
# 				if not fileinfo:
# 					break
# 				bytes = bytes + len(fileinfo)
# 				sock.send(fileinfo)
# 			sock.send(cfg.TIP_INFO_EOF)
# 			rtn = cfg.CMD_SUCC
# 		except Exception as e:
# 			rtn = cfg.CMD_FAIL
# 			print '-----  Upload Failed ------'
# 			print(traceback.format_exc())
# 		finally:
# 			return rtn
#
# 	def downloadFile(self, sock, FileSrc, FileDst):
# 		try:
# 			sock.send(genFReqHead(FileSrc) + cfg.TIP_INFO_EOF)
# 			rsp = recv_end(sock)
# 			head_info, buf = getFRspHead(rsp)
# 			print(head_info)
# 			print('++++++++')
# 			print(buf)
# 			seq_id, filename, status = getFRspInfo(head_info.strip())
# 			print(filename, status)
# 			if int(status) == cfg.CMD_SUCC:
# 				## dir exsit?
# 				f = open(FileDst, 'w')
# 				f.write(buf)
# 				f.close()
# 				rtn = cfg.CMD_SUCC
# 			else:
# 				rtn = cfg.CMD_FAIL
# 		except Exception as e:
# 			rtn = cfg.CMD_FAIL
# 			print(traceback.format_exc())
# 		finally:
# 			return rtn
#
# 	#一键发布
# 	def update_srv(self, request, ENV_KEY, delay_time):
# 		start_time = int(time.time())
# 		myFile = request.FILES['file']
# 		output_msg('myFile', request.FILES)
# 		output_msg('ENV_KEY', ENV_KEY)
# 		output_msg('delay_time', delay_time)
#
# 		exec_time = start_time + int(delay_time)
# 		rsp = ''
# 		status = "Failed"
# 		upload_time = -1
#
# 		if myFile:
# 			filepath = os.path.join(cfg.WORK_PATH_TEMP, myFile.name)
# 			output_msg('filepath: ', filepath)
# 			destination = open(filepath,'wb+')
# 			for chunk in myFile.chunks():
# 				destination.write(chunk)
# 			destination.close()
# 			daemaon_ip, daemon_port = getKey(ENV_KEY)
# 			sock = sock_conn(daemaon_ip, daemon_port)
#
# 			rtn = self.uploadFile(sock, filepath, str(exec_time))
# 			end_time = int(time.time())
# 			upload_time = str(end_time - start_time)
# 			if rtn == cfg.CMD_SUCC:
# 				rsp = recv_end(sock)
# 				status = 'Successful'
# 			sock.close()
#
# 			rsp_data = {'status': status,
# 						'time': upload_time,
# 						'info': rsp}
# 			output_msg('rsp_data', rsp_data)
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
# 		else:
# 			rsp_data = {'status': status,
# 						'time': upload_time,
# 						'info': "no files for upload!"}
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
#
#
# 	# @csrf_protect
# 	def upload_file(self, request, ENV_KEY):
# 		start_time = int(time.time())
# 		myFile = request.FILES['file']
# 		output_msg('myFile', request.FILES)
# 		output_msg('ENV_KEY', ENV_KEY)
# 		rsp = ''
# 		status = "Failed"
# 		upload_time = -1
# 		if myFile:
# 			filepath = os.path.join(cfg.WORK_PATH_TEMP, myFile.name)
# 			filedst = filepath + cfg.DOT + cfg.PID
# 			output_msg('filepath: ', filepath)
# 			output_msg('filedst: ', filedst)
#
# 			destination = open(filepath,'wb+')
# 			for chunk in myFile.chunks():
# 				destination.write(chunk)
# 			destination.close()
# 			daemaon_ip, daemon_port = getKey(ENV_KEY)
# 			sock = sock_conn(daemaon_ip, daemon_port)
# 			rtn = self.uploadFile(sock, filepath, filedst)
# 			end_time = int(time.time())
# 			upload_time = str(end_time - start_time)
#
# 			if rtn == cfg.CMD_SUCC:
# 				rsp = recv_end(sock)
# 				status = "Successful"
# 			sock.close()
# 			rsp_data = {'status': status,
# 						'time': upload_time,
# 						'info': rsp}
# 			output_msg('rsp_data', rsp_data)
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
# 		else:
# 			rsp_data = {'status': status,
# 						'time': upload_time,
# 						'info': "no files for upload!"}
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
#
# 	# @csrf_protect
# 	def download_file(self, request):
# 		FileName = request.POST.get('filename',None)
# 		status = "Failed"
# 		if FileName:
# 			daemaon_ip, daemon_port = getKey(ENV_KEY)
# 			sock = sock_conn(daemaon_ip, daemon_port)
# 			FileSrc = FileName
# 			FileDst = os.path.join(cfg.WORK_PATH_TEMP, FileName)
# 			FileNew = FileDst + cfg.DOT +cfg.PID
# 			FileNewDst = os.path.join(cfg.WORK_PATH_CFG, FileName + cfg.DOT + cfg.PID)
# 			rtn = self.downloadFile(sock, FileSrc, FileDst)
# 			sock.close()
# 			if rtn == cfg.CMD_SUCC:
# 				daemaon_ip, daemon_port = getKey(ENV_KEY)
# 				sock = sock_conn(daemaon_ip, daemon_port)
# 				shutil.copyfile(FileDst, FileNew)
# 				f = open(FileNew, "a+")
# 				f.write("## Add Test Info by " + str(cfg.PID) + ' \n')
# 				f.close()
# 				uploadFile(sock, FileNew, FileNewDst)
# 				status = "Success"
# 				sock.close()
# 			else:
# 				status = "Failed"
# 			rsp_data = {'status': status}
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
# 		else:
# 			rsp_data = {'status': status}
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
#
# 	def upload_file_b(self, request):
# 		rsp_data = {}
# 		if request.method == 'POST':
# 			start_time = int(time.time())
# 			upload_file = request.FILES['file']
# 			if upload_file:
# 				filename = str(upload_file).encode('utf-8')
# 				filepath = os.path.join(cfg.WORK_PATH_TEMP, filename)
# 				filedst = filepath + cfg.DOT + cfg.PID
# 				print 'filepath: ', filepath
# 				print 'filedest: ', filedst
#
# 				destination = open(filepath,'wb+')
# 				for chunk in upload_file.chunks():
# 					destination.write(chunk)
# 				destination.close()
# 				daemaon_ip, daemon_port = getKey(ENV_KEY)
# 				sock = sock_conn(daemaon_ip, daemon_port)
# 				rtn = self.uploadFile(sock, filepath, filedst)
# 				end_time = int(time.time())
#
# 				status = ''
# 				upload_time = str(end_time - start_time)
# 				print 'rtn: ', rtn
# 				if rtn == cfg.CMD_SUCC:
# 					rsp = recv_end(sock)
# 					status = "Successful"
# 				else:
# 					status = 'Failed'
# 				print 'status: ', status
# 				sock.close()
# 				rsp_data = {
# 					'type': status,
# 					'upload_time': upload_time
# 				}
# 			else:
# 				rsp_data = {
# 					'type': 'Failed',
# 					'info': 'No upload file'
# 				}
# 		else:
# 			rsp_data = {
# 				'type': 'Failed',
# 				'info': 'Is Not POST Requset!'
# 			}
# 		return HttpResponse(json.dumps(rsp_data), content_type = "application/json")

class AdminDataAjaxFunc(object):
	def set_dbdata(self, request):
		tmp_data = Person(name='LSZ', age=27)
		tmp_data.save()

		# for group_data in g_groups:
		# 	print group_data.name
		# 	print group_data.permission
		# 	db_obj = GroupInfo(name = group_data.name, permission = group_data.permission)
		# 	db_obj.save()

		for user in g_users:
			db_obj = UserInfo(name = user.name, email=user.email, \
			                  permission = user.permission, groups = user.groups)
			db_obj.save()
		rsp_data = {'data': 'set database data!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def get_dbdata(self, request):
		# person_obj = Person.objects.all()
		# result = {
		# 	'name': person_obj[0].name,
		# 	'age': person_obj[0].age
		# }

		group_array = []
		group_obj = GroupInfo.objects.all()

		for tmp_obj in group_obj:
			group_array.append(Group(tmp_obj.name, tmp_obj.permission).__dict__)

		rsp_data = {'data': group_array}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def request_user_login(self, request):
		req_json = request.POST.getlist('req_json')[0]
		req_json = json.loads(req_json)
		print req_json
		user_name = req_json['name']
		user_password = req_json['password']
		rsp_data = {}
		status = ''
		info = ''
		permission = ''
		try:
			user = UserInfo.objects.get(name = user_name)
			if user:
				password = user.password
				if password == user_password:
					status = 'Success'
					permission = user.permission
				else:
					status = 'Failed'
					info = '密码错误'
			rsp_data = {
				'status': status,
				'info': info,
				'permission': permission
			}
			response = HttpResponse(json.dumps(rsp_data))
			response["Access-Control-Allow-Origin"] = "*"
			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
			response["Access-Control-Max-Age"] = "1000"
			response["Access-Control-Allow-Headers"] = "*"
			return response
		except Exception as e:
			status = 'Failed'
			info = '用户不存在'
			rsp_data = {
				'status': status,
				'info': info
			}
			response = HttpResponse(json.dumps(rsp_data))
			response["Access-Control-Allow-Origin"] = "*"
			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
			response["Access-Control-Max-Age"] = "1000"
			response["Access-Control-Allow-Headers"] = "*"
			return response

	def set_chosen_group(self, request):
		group_name = request.POST.getlist('req_json')[0]
		group_name = group_name.encode('utf-8')
		print 'group_name:   ', group_name
		group = GroupInfo.objects.filter(name = group_name)
		print 'group_id:  ', group[0].id
		rsp_url = ''
		error_info = ''
		if group:
			rsp_url = '/admin/auth/group/' + str(group[0].id) + '/change'
		else:
			error_info = 'request name does not exit!'

		rsp_data = {'data': rsp_url,
					'error': error_info}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def set_chosen_user(self, request):
		userName = request.POST.getlist('req_json')[0]
		userName = userName.encode('utf-8')
		print 'userName:   ', userName
		user = UserInfo.objects.filter(name = userName)[0]
		print 'user_id:  ', user.id
		rsp_url = ''
		error_info = ''
		if user:
			rsp_url = '/admin/auth/user/' + str(user.id) + '/change'
		else:
			error_info = 'request name does not exit!'

		rsp_data = {'data': rsp_url,
					'error': error_info}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def delete_group_data(self, request):
		delete_data = request.POST.getlist('req_json')
		print delete_data
		successful_delete_data = []
		failed_delete_data = []
		for value in delete_data:
			if GroupInfo.objects.filter(name = value).delete():
				successful_delete_data.append(value)
			else:
				failed_delete_data.append(value)

		rsp_data = {'successful': successful_delete_data,
					'failed': failed_delete_data}
		print rsp_data
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def delete_user_data(self, request):
		delete_data = request.POST.getlist('req_json')
		successful_delete_data = []
		failed_delete_data = []
		for value in delete_data:
			if UserInfo.objects.filter(name = value).delete():
				successful_delete_data.append(value)
			else:
				failed_delete_data.append(value)

		rsp_data = {'successful': successful_delete_data,
					'failed': failed_delete_data}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def add_group_data(self, request):
		add_data = request.POST.getlist('req_json')[0]
		trans_add_data = json.loads(add_data)
		print trans_add_data
		status = ''
		info = ''
		if GroupInfo.objects.filter(name = trans_add_data['name']):
			status = 'Failed'
			info = '同名群组已存在'
		else:
			add_group = GroupInfo(name = trans_add_data['name'], permission = trans_add_data['permission'])
			add_group.save()
			status = 'Successful'

		rsp_data = {'status': status,
					'info': info}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def add_user_data(self, request):
		add_data = request.POST.getlist('req_json')[0]
		trans_add_data = json.loads(add_data)
		print trans_add_data
		status = ''
		info = ''
		if UserInfo.objects.filter(name = trans_add_data['name']):
			status = 'Failed'
			info = '用户已经存在！'
		else:
			add_user = UserInfo(name = trans_add_data['name'], password = trans_add_data['password'])
			add_user.save()
			status = 'Successful'

		rsp_data = {'status': status,
					'info': info}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def change_group_data(self, request):
		change_data = request.POST.getlist('req_json')[0]
		trans_change_data = json.loads(change_data)
		print trans_change_data
		status = ''
		info = ''
		# try:
		group = GroupInfo.objects.filter(id = int(trans_change_data['group_id']))[0]
		print group
		if trans_change_data['name'] != group.name:
			all_group = GroupInfo.objects.all()
			for tmpGroup in all_group:
				if tmpGroup.name == trans_change_data['name']:
					status = 'Failed'
					info = '群组已经存在'
			if info == '':
				all_user = UserInfo.objects.all()
				for tmpUser in all_user:
					if group.name in tmpUser.groups:
						print 'Groups changed User: ', tmpUser.name
						tmpUser_groups = tmpUser.groups
						user_group_array = tmpUser_groups.split(';')
						user_group_array.remove(group.name)
						user_permission_array = []
						for tmpGroup_name in user_group_array:
							tmpGroup = GroupInfo.objects.filter(name = tmpGroup_name)[0]
							tmpPermission_array = tmpGroup.permission.split(';')
							for tmpPermission in tmpPermission_array:
								if tmpPermission not in user_permission_array:
									user_permission_array.append(tmpPermission)
						new_group_permission_array = trans_change_data['permission'].split(';')
						if '' in new_group_permission_array:
							new_group_permission_array.remove('')

						output_msg('user_permission_array: ', user_permission_array)
						output_msg('new_group_permission_array: ', new_group_permission_array)

						for new_tmpPermission in new_group_permission_array:
							if new_tmpPermission not in user_permission_array:
								user_permission_array.append(new_tmpPermission)

						output_msg('user_permission_array: ', user_permission_array)
						new_user_permission = ';'.join(user_permission_array)
						# output_msg('new_user_permission: ', new_user_permission)
						output_msg('tmpUser_groups: ', tmpUser_groups)
						new_user_groups = tmpUser_groups.replace(group.name, trans_change_data['name'])
						output_msg('new_user_groups: ', new_user_groups)
						UserInfo.objects.filter(name = tmpUser.name).update(groups = new_user_groups)
						UserInfo.objects.filter(name = tmpUser.name).update(permission = new_user_permission)

		if info == '':
			status = 'Successful'
			group.permission = trans_change_data['permission']
			group.name = trans_change_data['name']
			group.save()

		# except Exception as e:
		# 	status = 'Failed'
		# 	info = '群组不存在'

		rsp_data = {'status': status,
					'info': info}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def change_user_data(self, request):
		change_data = request.POST.getlist('req_json')[0]
		trans_change_data = json.loads(change_data)
		print trans_change_data
		status = ''
		info = ''
		alive_group = []
		try:
			user =  UserInfo.objects.filter(id = trans_change_data['user_id'])[0]
			if trans_change_data['name'] != user.name :
				all_user = UserInfo.objects.all()
				for tmpUser in all_user:
					if tmpUser.name == trans_change_data['name']:
						status = 'Failed'
						info = '存在同名用户'
			if info == '':
				status = 'Successful'
				user_permission_array = []
				group_array = trans_change_data['groups'].split(';')
				group_array.remove('')
				for group_name in group_array:
					# print len(group_name)
					# group_name = group_name[1:len(group_name)-1]
					# print len(group_name)
					group = GroupInfo.objects.get(name = group_name)
					if group:
						# print 'Alive Group'
						alive_group.append(group_name)
						group_permission = group.permission
						group_permission_array = group_permission.split(';')
						for permission in group_permission_array:
							if permission not in user_permission_array:
								user_permission_array.append(permission)

				user.permission = ';'.join(user_permission_array)
				user.groups = ';'.join(alive_group)
				user.name = trans_change_data['name']
				user.email = trans_change_data['email']
				user.save()

		except Exception as e:
			status = 'Failed'
			info = '用户不存在'

		rsp_data = {'status': status,
					'info': info}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def change_user_password(self, request):
		change_data = request.POST.getlist('req_json')[0]
		trans_change_data = json.loads(change_data)
		output_msg('trans_change_data: ', trans_change_data)
		user_name = trans_change_data['name']
		old_password = trans_change_data['old_password']
		new_password = trans_change_data['new_password']
		status = 'Success'
		error = ''
		info = ''
		user =  UserInfo.objects.get(name = user_name)
		if old_password != user.password:
			status = 'Failed'
			error = '旧密码不正确'
		else:
			info = '/admin/auth/'
			user.password = new_password
			user.save()

		rsp_data = {'status': status,
					'info': info,
					'error': error}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

# class TaskAjaxFunc(object):
# 	def get_task_type(self, trans_req_json):
# 		task_type = cfg.TASK_TYPE_ECALL
# 		cmdline = ''
# 		if 'type' in trans_req_json and trans_req_json['type'] == 'version_control':
# 			data_type = 'version_control_' + trans_req_json['--cmd']
# 			task_type = cfg.TASK_TYPE_VERCONTROL
# 		elif '--args' not in trans_req_json or trans_req_json['--args'] == '' or \
# 			trans_req_json['--args'] =='app':
# 			data_type = 'default'
# 		else:
# 			data_type = trans_req_json['--args']
# 		req_para = ['--cmd', '--args', '--grp', \
# 					'--ctr', '--srv', '--srvno',\
# 					'--ictr', '--isrv', '--isrvno']
# 		for value in req_para:
# 			if value in req_para and value in trans_req_json and trans_req_json[value] !='':
# 				cmdline += value + ' ' + trans_req_json[value] + ' '
#
# 		cmdline = cmdline[len('--cmd '):]
#
# 		print '\ndata_type: ', data_type
# 		print 'task_type: ', task_type
# 		print ('The REQUEST command line is: %s\n' %(cmdline))
# 		return {
# 			'data_type': data_type,
# 			'task_type': task_type,
# 			'cmdline': cmdline,
# 			'cmd': trans_req_json['--cmd']
# 		}
#
# 	@csrf_exempt
# 	def request_real_time_info_task(self, request):
# 		if request.method != '':
# 			req_json = request.POST.getlist('req_json')[0]
# 			trans_req_json = json.loads(req_json)
# 			output_msg('Original Req_json!', req_json)
# 			output_msg('Transed Req_Json!', trans_req_json)
#
# 			compact_req_json = {}
# 			for key in trans_req_json:
# 				if key != 'ENV_KEY' and trans_req_json[key] != '':
# 					if key.find('--') == 0:
# 						trans_key = key[2:]
# 						compact_req_json[trans_key] = trans_req_json[key]
# 					else:
# 						compact_req_json[key] = trans_req_json[key]
# 			compact_req_json = str(compact_req_json)
# 			eval_req_json = eval(compact_req_json)
# 			output_msg('Str Compact Req_JSON', compact_req_json)
#
# 			ENV_KEY = trans_req_json['ENV_KEY']
# 			req_data = self.get_task_type(trans_req_json)
# 			data_type = req_data['data_type']
# 			task_type = req_data['task_type']
# 			rsp = ''
# 			original_rsp_data = ''
# 			trans_rsp_data = {}
# 			args = 'relay'
#
# 			try:
# 				daemaon_ip, daemon_port = getKey(ENV_KEY)
# 				sock = sock_conn(daemaon_ip, daemon_port)
# 				# sock.send(genCmdInfoHead() + args + cfg.TIP_INFO_EOF)
# 				sock.send(genCmdInfoHead() + compact_req_json + cfg.TIP_INFO_EOF)
# 				original_rsp_data = recv_end(sock)
# 				output_msg('The original rsp data is: ', original_rsp_data)
# 				sock.close()
# 				trans_rsp_data = self.process_rpc_result(original_rsp_data, data_type)
#
# 				output_msg('Transed Rsp Data: ', trans_rsp_data)
# 			except Exception as e:
# 				print('notifyDaemon failed!')
# 				print(traceback.format_exc())
#
# 			response = HttpResponse(json.dumps(trans_rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
# 		else:
# 			return index(request)
#
# 	@csrf_exempt
# 	def request_real_time_versionCtr_task(self, request):
# 		if request.method != '':
# 			req_json = request.POST.getlist('req_json')[0]
# 			output_msg('req_json', req_json)
# 			trans_req_json = json.loads(req_json)
# 			output_msg('trans_req_json', trans_req_json)
#
# 			ENV_KEY = trans_req_json['ENV_KEY']
# 			req_data = self.get_task_type(trans_req_json)
# 			data_type = req_data['data_type']
# 			task_type = req_data['task_type']
# 			cmdline = req_data['cmdline']
# 			cmd = req_data['cmd']
#
# 			original_rsp_data = ''
# 			task_info = TaskInfo(state=cfg.FLAG_TASK_READY, TID=0, PID=int(cfg.PID), exec_time=0, \
# 						cmd=cmd.strip(), cmdline=cmdline.strip(), task_type=int(task_type))
# 			trans_rsp_data = {}
# 			try:
# 				daemaon_ip, daemon_port = getKey(ENV_KEY)
# 				sock = sock_conn(daemaon_ip, daemon_port)
# 				sock.send(genRpcHead() + task_info.encode() + cfg.TIP_INFO_EOF)
# 				original_rsp_data = recv_end(sock)
# 				sock.close()
# 				output_msg('original_rsp_data: ', original_rsp_data)
# 				trans_rsp_data = self.process_rpc_result(original_rsp_data, data_type)
# 				output_msg('trans_rsp_data: ', trans_rsp_data)
# 			except Exception as e:
# 				print('notifyDaemon failed!')
# 				print(traceback.format_exc())
# 			rsp_data = trans_rsp_data
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
# 		else:
# 			response = HttpResponse(json.dumps({'info': 'Request is fasle!'}))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
#
# 	def request_ntf_task(self, request):
# 		if request.method != '':
# 			req_json = request.POST.getlist('req_json')[0]
# 			trans_req_json = json.loads(req_json)
#
# 			ENV_KEY = trans_req_json['ENV_KEY']
# 			req_data = self.get_task_type(trans_req_json)
# 			data_type = req_data['data_type']
# 			cmdline = req_data['cmdline']
# 			task_type = req_data['task_type']
# 			cmd = req_data['cmd']
#
# 			output_msg('Original Req_json!', req_json)
# 			output_msg('Transed Req_Json!', trans_req_json)
#
# 			tasktime = int(time.time()) + trans_req_json['exec_time']
# 			task_info = TaskInfo(state = cfg.FLAG_TASK_READY, TID = 0, PID = int(cfg.PID), exec_time=tasktime, \
# 								 cmd = cmd.strip(), cmdline = cmdline.strip(), task_type = int(task_type))
# 			# if cmdline.find(cfg.SEMICOLON) != -1:
# 			# 	task_type, cmdline = cmdline.split(cfg.SEMICOLON)  ##命令行中有分号
# 			# else:
# 			# 	task_type = cfg.TASK_TYPE_ECALL
# 			# 	task_info = TaskInfo(state=cfg.FLAG_TASK_READY, TID=0, PID=int(cfg.PID), exec_time=tasktime, \
# 			# 						 cmd=cmd.strip(), cmdline=cmdline.strip(), task_type=int(task_type))
# 			try:
# 				daemaon_ip, daemon_port = getKey(ENV_KEY)
# 				sock = sock_conn(daemaon_ip, daemon_port)
# 				sock.send(genNtfHead() + task_info.encode() + cfg.TIP_INFO_EOF)
# 				sock.close()
#
# 				output_msg('task_info: ', task_info.__dict__)
# 			except Exception as e:
# 				print('notifyDaemon failed!')
# 				print((traceback.format_exc()))
#
# 			rsp_data = {'task_info': task_info.__dict__,
# 						'data_type': data_type}
# 			rsp_data = [task_info.TID, data_type]
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
# 		else:
# 			return index(request)
#
# 	def get_nft_task_state(self, ENV_KEY, task_id = 0):
# 		req_info = ReqInfo(task_id, cfg.FLAG_REQTYPE_TASKINFO)
# 		rsp = ''
# 		task_list = []
# 		try:
# 			daemaon_ip, daemon_port = getKey(ENV_KEY)
# 			sock = sock_conn(daemaon_ip, daemon_port)
# 			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
# 			rsp = recv_end(sock)
# 			print rsp
# 			rsp_list = rsp.split("\n")
# 			for token in rsp_list:
# 				if token.startswith(cfg.TIP_INFO_TASK):
# 					info = token[len(cfg.TIP_INFO_TASK):]
# 					task_info = TaskInfo()
# 					task_info.decode(info)
# 					if task_id == 0:
# 						task_list.append(task_info.__dict__)
# 					else:
# 						task_list = task_info.__dict__
#
# 			if task_id == 0:
# 				for info in task_list:
# 					print info
# 			else:
# 				output_msg('task_list: ', task_list)
# 				# print task_list
#
# 			sock.close()
# 		except Exception as e:
# 			print('notifyDaemon failed!')
# 			print(traceback.format_exc())
# 		return task_list
#
# 	def get_nft_task_result(self, ENV_KEY, task_id = 0):
# 		req_info = ReqInfo(task_id, cfg.FLAG_REQTYPE_TASKRESULT)
# 		task_result = ''
# 		trans_result = {}
# 		try:
# 			daemaon_ip, daemon_port = getKey(ENV_KEY)
# 			sock = sock_conn(daemaon_ip, daemon_port)
# 			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
# 			task_result = recv_end(sock)
# 			sock.close()
# 			if task_id == 0:
# 				task_result = task_result.split('\n')
# 				trans_result = eval(task_result[1])
# 				output_msg('Transed Rsp Data:', trans_result, type(trans_result))
# 				output_msg('Original Rsp Data:', task_result, type(task_result))
# 			else:
# 				trans_result = task_result
# 				output_msg('Original Rsp Data:', trans_result)
# 		except Exception as e:
# 			print('notifyDaemon failed!')
# 			print(traceback.format_exc())
# 		return trans_result
#
# 	def get_all_ntf_task_result(self, request):
# 		if request.method != '':
# 			req_data = request.POST.getlist('req_json')[0]
# 			req_data = json.loads(req_data)
#
# 			task_data = req_data['task_data']
# 			ENV_KEY = req_data['ENV_KEY']
#
# 			output_msg('req_json', req_data)
# 			output_msg('task_data', task_data)
#
# 			task_type = {}
# 			task_result = {}
# 			# 遍历客户请求
# 			index  = 0
# 			while index < len(task_data):
# 				# task_data[index] = task_data[index].split(',')
# 				task_id = task_data[index][0]
# 				task_type[task_id] = task_data[index][1]
# 				task_info = self.get_nft_task_state(ENV_KEY, task_id)
# 				if task_info == []:
# 					break
# 				if task_info['state'] == 3:
# 					task_result[task_id] = self.get_nft_task_result(ENV_KEY, task_id)
# 					task_result[task_id] = self.process_rpc_result(task_result[task_id], task_type[task_id])
# 				elif task_info['state'] == 1:
# 					task_result[task_id] = 'Failed'
# 				else:
# 					task_result[task_id] = 'Empty'
# 				index += 1
# 			output_msg('task_result', task_result)
#
# 			# 全遍历
# 			# task_info = self.get_nft_task_state()
# 			# for task in task_info:
# 			# 	task_id = task['TID']
# 			# 	if task['state'] == 3:
# 			# 		task_result[task_id] = self.get_nft_task_result(task_id)
#
# 			rsp_data = {'task_result': task_result}
#
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
# 		else:
# 			response = HttpResponse(json.dumps('wrong!'))
# 			return response
#
# 	def get_all_ntf_task_state(self, request):
# 		if request.method != '':
# 			req_data = request.POST.getlist('req_json')[0]
# 			req_data = json.loads(req_data)
# 			ENV_KEY = req_data['ENV_KEY']
#
# 			task_info = self.get_nft_task_state(ENV_KEY)
# 			rsp_data = {'task_info': task_info}
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
# 		else:
# 			response = HttpResponse(json.dumps('wrong!'))
# 			return response
#
# 	@csrf_exempt
# 	def test_task_rpc(self, request):
# 		if request.method != '':
# 			req_json = request.POST.getlist('req_json')[0]
# 			print req_json
# 			trans_req_json = json.loads(req_json)
# 			print trans_req_json
#
# 			req_data = self.get_task_type(trans_req_json)
# 			data_type = req_data['data_type']
# 			task_type = req_data['task_type']
# 			cmdline = req_data['cmdline']
#
# 			original_rsp_data = ''
# 			cmd = 'info'
# 			task_info = TaskInfo(state=cfg.FLAG_TASK_READY, TID=0, PID=int(cfg.PID), exec_time=0, \
# 						cmd=cmd.strip(), cmdline=cmdline.strip(), task_type=int(task_type))
# 			trans_rsp_data = {}
# 			try:
# 				daemaon_ip, daemon_port = getKey(ENV_KEY)
# 				sock = sock_conn(daemaon_ip, daemon_port)
# 				sock.send(genRpcHead() + task_info.encode() + cfg.TIP_INFO_EOF)
# 				original_rsp_data = recv_end(sock)
# 				sock.close()
# 				print ('The original rsp data is:\n%s' %(original_rsp_data))
# 				trans_rsp_data = self.process_rpc_result(original_rsp_data, data_type)
# 				print 'Transed Rsp Data: '
# 				print trans_rsp_data
# 			except Exception as e:
# 				print('notifyDaemon failed!')
# 				print(traceback.format_exc())
# 			rsp_data = trans_rsp_data
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
# 		else:
# 			return index(request)
#
# 	def test_all_srvstatus(self, request):
# 		if request.method != '':
# 			req_info = ReqInfo(0, cfg.FLAG_REQTYPE_SRVSTATUS)
# 			rsp = ''
# 			try:
# 				# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 				# sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
# 				daemaon_ip, daemon_port = getKey(ENV_KEY)
# 				sock = sock_conn(daemaon_ip, daemon_port)
# 				sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
# 				rsp = recv_end(sock)
# 				print 'Test_all_srvstatus'
# 				print rsp
# 				sock.close()
# 				rsp_list = rsp.split("\n")
# 				SrvStatus_list = []
# 				for token in rsp_list:
# 					if token.startswith(cfg.TIP_BODY_REQ):
# 						info = token[len(cfg.TIP_BODY_REQ):]
# 						srv_status = SrvStatus()
# 						srv_status.decode(info)
# 						SrvStatus_list.append(srv_status.__dict__)
# 				# for info in SrvStatus_list:
# 				# 	print(info.encode())
# 				rsp_data = SrvStatus_list
# 			except Exception as e:
# 				print('notifyDaemon failed!')
# 				print(traceback.format_exc())
# 			# return HttpResponse(json.dumps(rsp_data), content_type = "application/json")
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
# 		else:
# 			return index(request)
#
# 	def test_all_tasklist(self, request):
# 		#if request.method == 'POST':
# 		if request.method != '':
#
# 			#从POST请求中获取查询关键字
# 			###
# 			req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKLIST)
# 			rsp_data = ''
# 			try:
# 				# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 				# sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
# 				daemaon_ip, daemon_port = getKey(ENV_KEY)
# 				sock = sock_conn(daemaon_ip, daemon_port)
# 				sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
# 				rsp = recv_end(sock)
# 				print rsp
# 				rsp_list = rsp.split("\n")
# 				task_list = []
# 				for token in rsp_list:
# 					if token.startswith(cfg.TIP_INFO_TASK):
# 						info = token[len(cfg.TIP_INFO_TASK):]
# 						task_info = TaskInfo()
# 						task_info.decode(info)
# 						task_list.append(task_info.__dict__)
# 				# for info in task_list:
# 				# 	print(info.encode())
# 				sock.close()
# 				rsp_data = task_list
# 			except Exception as e:
# 				print('notifyDaemon failed!')
# 				print(traceback.format_exc())
# 			# return HttpResponse(json.dumps(rsp_data), content_type = "application/json")
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
# 		else:
# 			return index(request)
#
# 	def test_all_taskresult(self, request):
# 		if request.method != '':
# 			print 'test_all_taskresult!'
# 			req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKRESULT)
# 			task_result = ''
# 			trans_result = {}
# 			try:
# 				# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 				# sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
# 				daemaon_ip, daemon_port = getKey(ENV_KEY)
# 				sock = sock_conn(daemaon_ip, daemon_port)
# 				sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
# 				task_result = recv_end(sock)
# 				sock.close()
#
# 				task_result = task_result.split('\n')
# 				trans_result = eval(task_result[1])
#
# 				output_msg('Original Rsp Data:', task_result[1], type(task_result[1]))
# 				output_msg('Transed Rsp Data:', trans_result, type(trans_result))
# 			except Exception as e:
# 				print('notifyDaemon failed!')
# 				print(traceback.format_exc())
# 			rsp_data = {'task_result': trans_result}
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
# 		else:
# 			return index(request)
#
# 	def test_all_version(self, request):
# 		if request.method != '':
# 			req_data = request.POST.getlist('req_json')[0]
# 			req_data = json.loads(req_data)
# 			ENV_KEY = req_data['ENV_KEY']
#
# 			req_info = ReqInfo(0, cfg.FLAG_REQTYPE_VERSION)
# 			rsp = ''
# 			rsp_data = ''
# 			try:
# 				daemaon_ip, daemon_port = getKey(ENV_KEY)
# 				sock = sock_conn(daemaon_ip, daemon_port)
# 				sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
# 				tcp_send_head = genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF
#
# 				rsp = recv_end(sock)
# 				sock.close()
# 				rsp_list = rsp.split("\n")
# 				version_list = []
#
# 				for token in rsp_list:
# 					if token.startswith(cfg.TIP_BODY_VERINFO):
# 						info = token[len(cfg.TIP_BODY_VERINFO):]
# 						version_info = VersionInfo()
# 						version_info.decode(info)
# 						version_list.append(version_info.__dict__)
# 				if info in version_list:
# 					print info
# 				rsp_data = version_list
# 			except Exception as e:
# 				print('notifyDaemon failed!')
# 				print(traceback.format_exc())
#
# 			response = HttpResponse(json.dumps(rsp_data))
# 			response["Access-Control-Allow-Origin"] = "*"
# 			response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
# 			response["Access-Control-Max-Age"] = "1000"
# 			response["Access-Control-Allow-Headers"] = "*"
# 			return response
# 		else:
# 			return index(request)
#
# 	def process_rpc_result(self, origin_data, data_type):
# 		failed_data = self.get_failed_data(origin_data, data_type)
# 		if failed_data == '':
# 			array_data = []
# 			if is_version_control_req(data_type):
# 				array_data = self.get_version_ctr_array_result(origin_data, data_type)
# 			else:
# 				array_data = self.get_task_rpc_array_result(origin_data)
#
# 			# output_msg('array_data', array_data)
# 			dict_data = self.get_rpc_dict_result(array_data, data_type)
# 			return {'data': dict_data, 'type': data_type}
# 		else:
# 			return {'data': failed_data, 'type': 'Failed'}
#
# 	def get_failed_data(self, origin_data, data_type):
# 		tmpdata = origin_data.split('\n')
# 		if '' in tmpdata:
# 			tmpdata.remove('')
# 		verControl_param_wrong_flag = 'verControl Usage:'
# 		main_param_wrong_flag = 'main Usage:'
#
# 		if is_version_control_req(data_type):
# 			verControl_SUCC_flag = '--------'
# 			if tmpdata[1].find('verControl Usage:') != -1:
# 				failed_data = 'verControl Failed'
# 			else:
# 				failed_data = tmpdata[1:]
# 				for value in tmpdata:
# 					if value.find(verControl_SUCC_flag) != -1:
# 						failed_data = ''
# 						break
# 		else:
# 			failed_data = ''
# 		return failed_data
#
# 	def get_version_ctr_array_result(self, origin_data, data_type):
# 		tmpdata = origin_data.split('\n')
# 		array_data = []
# 		tmpdata = tmpdata[len(tmpdata)-2].split('\t')
# 		array_data.append(tmpdata)
# 		# if data_type.find('show')!= -1 or data_type.find('rollback')!= -1 or data_type.find('drop')!= -1:
# 		# 	tmpdata = tmpdata[len(tmpdata)-2].split('\t')
# 		# 	array_data.append(tmpdata)
# 		# else:
# 		# 	array_data.append(tmpdata[1:])
#
# 		return array_data
#
# 	def get_version_ctr_array_result_back(self, origin_data, data_type):
# 		tmpdata = origin_data.split('\n')
# 		tmpdata = tmpdata[1:len(tmpdata)-1]
# 		index = 0
# 		info_flag = ': '
# 		other_flag = '::'
# 		output_msg('tmpdata', tmpdata)
# 		final_result = []
# 		while index < len(tmpdata):
# 			tmp_result = []
# 			if tmpdata[index].find(other_flag) >= 0:
# 				tmpdata[index] = tmpdata[index][tmpdata[index].find(other_flag) + len(other_flag):]
# 				tmpdata[index] = tmpdata[index].split(other_flag)
# 			elif tmpdata[index].find(info_flag) >= 0 :
# 				tmpdata[index] = tmpdata[index][tmpdata[index].find(info_flag) + len(info_flag):]
# 				tmpdata[index] = tmpdata[index].split(' ')
# 			for value in tmpdata[index]:
# 				if value != '':
# 					tmp_result.append(value)
# 			final_result.append(tmp_result)
# 			index += 1
# 		return final_result
#
# 	def get_task_rpc_array_result(self, origin_data):
# 		tmpdata = origin_data.split('\n')
# 		tmpdata = tmpdata[1:len(tmpdata)-1]
# 		index = 0
# 		info_flag = ': '
# 		other_flag = '::'
#
# 		final_result = []
# 		while index < len(tmpdata):
# 			tmp_result = []
# 			if tmpdata[index].find(other_flag) >= 0:
# 				tmpdata[index] = tmpdata[index][tmpdata[index].find(other_flag) + len(other_flag):]
# 				tmpdata[index] = tmpdata[index].split(other_flag)
# 			elif tmpdata[index].find(info_flag) >= 0:
# 				tmpdata[index] = tmpdata[index][tmpdata[index].find(info_flag) + len(info_flag):]
# 				tmpdata[index] = tmpdata[index].split(' ')
# 			for value in tmpdata[index]:
# 				if value != '':
# 					tmp_result.append(value)
# 			final_result.append(tmp_result)
# 			index += 1
# 		return final_result
#
# 	def get_rpc_dict_result(self, array_data, data_type):
# 		index = 0
# 		dict_data = []
# 		while index < len(array_data):
# 			tmp_dict_data = RpcResult(data_type, array_data[index])
# 			dict_data.append(tmp_dict_data.__dict__)
# 			index += 1
# 		return dict_data

class AjaxReqFunc(AdminDataAjaxFunc):
	def __init__ (self):
		self.name = 'AjaxReqFunc'

	def default_ajax_request(self, request):
		return HttpResponse(json.dumps({'data':'AJAX Request Failed!'}), content_type = "application/json")

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

	def get_admin_auth_group_object(self, id =''):
		group_array = []
		if id =='':
			group_obj = GroupInfo.objects.all()
			for tmp_obj in group_obj:
				group_array.append(Group(tmp_obj.name, tmp_obj.permission).__dict__)
		else:
			group_obj = GroupInfo.objects.get(name = id)
			if group_obj:
				group_array.append(Group(group_obj.name, group_obj.permission).__dict__)

		tmp_object = {
			'user': g_login_user,
			'groups': group_array,
			'group_numbs': len(group_array),
			'search_groupname': id
		}
		return tmp_object

	def get_admin_auth_group_add_object(self):
		tmp_object = {
			'available_permissions': g_group_permission
		}
		return tmp_object

	def get_admin_auth_group_change_object(self, cur_id = -1):
		group_json = {}
		if cur_id !=-1:
			group = GroupInfo.objects.filter(id = int(cur_id))[0]
			permission_array = []
			if group.permission == 'all':
				permission_array = g_group_permission
			elif group.permission != None:
				permission_array = group.permission.split(';')
				permission_array.remove('')

			group_json = {
				'name': group.name
			}
		tmp_object = {
			'login_user': g_login_user,
			'available_permissions': g_group_permission,
			'group': group_json,
			'permission': permission_array,
			'group_id': cur_id
		}
		return tmp_object

	def get_admin_auth_user_object(self, id=''):
		user_array = []
		if id == '':
			user_obj = UserInfo.objects.all()
			for tmp_obj in user_obj:
				user_array.append(User(tmp_obj.name, tmp_obj.email, \
				                  tmp_obj.permission, tmp_obj.groups).__dict__)
		else:
			user_obj = UserInfo.objects.get(name = id)
			if user_obj:
				user_array.append(User(user_obj.name, user_obj.email, \
				                  user_obj.permission, user_obj.groups, user_obj.password).__dict__)
		tmp_object = {
			'user': g_login_user,
			'users': user_array,
			'user_numb': len(user_array),
			'search_username': id
		}
		return tmp_object

	def get_admin_auth_user_add_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_auth_user_change_object(self, cur_id = -1):
		user_json = {}
		if cur_id !=-1:
			user = UserInfo.objects.filter(id = int(cur_id))[0]
			permission_array = []
			user_groups = []
			available_groups = []
			group_obj = GroupInfo.objects.all()

			for tmp_obj in group_obj:
				available_groups.append(Group(tmp_obj.name, tmp_obj.permission).name)
			print type(user.permission)
			# print user.permission
			if user.permission == 'all':
				permission_array = g_group_permission
			elif user.permission != None:
				permission_array = user.permission.split(';')
				if '' in permission_array:
					permission_array.remove('')

			if user.groups == 'all':
				user_groups = available_groups
			elif user.groups != None :
				user_groups = user.groups.split(';')
				if '' in user_groups:
					user_groups.remove('')

			user_json = {
				'name': user.name,
				'email': user.email
			}
		tmp_object = {
			'login_user': g_login_user,
			'user': user_json,
			'available_permissions': g_user_permission,
			'permission': permission_array,
			'available_groups': available_groups,
			'user_groups': user_groups,
			'user_id': cur_id
		}
		return tmp_object

server_view = ViewMain()
