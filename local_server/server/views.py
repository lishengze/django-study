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
from django.views.decorators.csrf import csrf_protect, csrf_exempt

import json
from models import Person
from models import GroupInfo
from models import UserInfo

g_users = {}
g_groups = {}
g_chosen_user = {}
g_chosen_group = {}
g_login_user = {}
g_env_array = []
g_group_permission = []
g_user_permission = []

class User(object):
	def __init__(self, name = 'tmp', email = 'tmp', permisson = 'all', groups = 'all'):
		self.name = name
		self.email = email
		self.permisson = permisson
		self.groups = groups
		self.__dict__ = {
			'name': self.name,
			'email': self.email,
			'permisson': self.permisson,
			'groups': self.groups
		}

class Group(object):
	def __init__(self, name = 'tmp', permisson = 'all'):
		self.name = name
		self.permisson = permisson
		self.__dict__ = {
			'name': self.name,
			'permisson': self.permisson
		}

def init_globals():
	global g_users, g_groups, g_login_user, g_env_array, g_get_html_object
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

	g_group_permission = ["admin | log entry | Can change log entry", \
						  "admin | log entry | Can add log entry", \
						  "admin | log entry | Can delete log entry", \
						  "auth | group | Can add group", \
						  "auth | group | Can change group", \
						  "auth | group | Can delete group", \
						  "auth | permission | Can add permission", \
						  "auth | permission | Can change permission", \
						  "auth | permission | Can delete permission", \
						  "auth | user | Can add user", \
						  "auth | user | Can change user", \
						  "auth | user | Can delete user", \
						  "contenttypes | content type | Can add content type", \
						  "contenttypes | content type | Can change content type", \
						  "contenttypes | content type | Can delete content type", \
						  "sessions | session | Can add session", \
						  "sessions | session | Can change session", \
						  "sessions | session | Can delete session"]
	g_user_permission = g_group_permission

init_globals()

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

	def is_static_file(self, file_name):
		name_array = file_name.split('/')
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

	def get_static_file_name(self, origin_file_name):
		name_array = origin_file_name.split('/')
		index = 0
		static_flag = 'static'
		for value in name_array:
			if value == static_flag:
				break
			index += 1
		trans_file_name = '/'.join(name_array[index:])
		return self.delete_headend_slash(trans_file_name)

	def get_html_file_name(self, path):
		name_array = path.split('/')
		return name_array[len(name_array)-1]

	def is_empty_html_request(self, file_name):
		name_array = file_name.split('/')
		last_file_name = name_array[len(name_array)-1]
		if last_file_name.find('.') == -1:
			return True
		else:
			return False

	def is_html_request(self, path_name):
		html_flag = '.html'
		flag = False
		if len(path_name) > len(html_flag) and path_name[-len(html_flag):] == html_flag:
			flag = True
		return flag

	def get_file_name(self, path):
		file_name = self.delete_headend_slash(path)
		html_flag = '.html'
		# if is_static_file(file_name):
		# 	file_name = get_static_file_name(file_name)
		if self.is_empty_html_request(file_name):
			file_name += html_flag
		return file_name

	def get_html_file_name_and_id(self, file_name):
		html_flag = '.html'
		file_name = file_name[:len(file_name)-len(html_flag)]
		file_name_array = file_name.split('/')
		if file_name_array[len(file_name_array)-1] == 'change' and file_name_array[len(file_name_array)-2].isdigit():
			data_id = file_name_array[len(file_name_array)-2]
			file_name_array.remove(file_name_array[len(file_name_array)-2])
			file_name = '/'.join(file_name_array)
			file_name = self.delete_headend_slash(file_name) + html_flag
			return {
				'id': data_id,
				'file_name': file_name,
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
			'Request_All_SrvStatus': self._ajax_func.test_all_srvstatus,
			'Request_All_TaskList': self._ajax_func.test_all_tasklist,
			'Request_All_TaskResult': self._ajax_func.test_all_taskresult,
			'Request_All_Version': self._ajax_func.test_all_version,
	        'Request_Task_Rpc': self._ajax_func.test_task_rpc,
	        'Request_Task_Ntf': self._ajax_func.test_task_ntf,
			'Upload_File': self._ajax_func.upload_file,
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
		}
		ajax_func = ajax_func_dict.get(ajax_name, self._ajax_func.default_ajax_request)
		return ajax_func

	def get_file_object(self, file_name, id = -1):
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
		object_func = file_object_dict.get(file_name, lambda :{})
		if id !=-1:
			print object_func(id)
			return object_func(id)
		else:
			print object_func()
			return object_func()

	@csrf_exempt
	def main_query_rsp(self, request):
		if self.is_ajax_request(request.path):
			print '\nIs AJAX Request'
			ajax_func = self.get_ajax_func(request.path)
			return ajax_func(request)
		else:
			print '\nIs not AJAX Request'
			file_name = self.get_file_name(request.path)
			file_object = {}
			if self.is_html_request(file_name):
				return_data = self.get_html_file_name_and_id(file_name)
				print return_data
				if return_data:
					file_name = return_data['file_name']
					file_object = self.get_file_object(file_name, return_data['id'])
				else:
					file_object = self.get_file_object(file_name)
			print 'file name: ' + file_name + '\n'
			return render(request, file_name, file_object)

class AdminDataAjaxFunc(object):
	def set_dbdata(self, request):
		tmp_data = Person(name='LSZ', age=27)
		tmp_data.save()

		# for group_data in g_groups:
		# 	print group_data.name
		# 	print group_data.permisson
		# 	db_obj = GroupInfo(name = group_data.name, permission = group_data.permisson)
		# 	db_obj.save()

		for user in g_users:
			db_obj = UserInfo(name = user.name, email=user.email, \
			                  permission = user.permisson, groups = user.groups)
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

	def delete_group_data(self, request):
		delete_data = request.POST.getlist('req_json')
		successful_delete_data = []
		failed_delete_data = []
		for value in delete_data:
			if GroupInfo.objects.filter(name = value).delete():
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
		if GroupInfo.objects.filter(name = trans_add_data['name']):
			status = 'Failed'
		else:
			add_group = GroupInfo(name = trans_add_data['name'], permission = trans_add_data['permission'])
			add_group.save()
			status = 'Successful'

		rsp_data = {'status': status}
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
		group = GroupInfo.objects.get(name = trans_change_data['name'])
		if group:
			status = 'Successful'
			group.permission = trans_change_data['permission']
			group.save()
		else:
			status = 'Failed'

		rsp_data = {'status': status}
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
		user = UserInfo.objects.get(name = trans_change_data['name'])
		if user:
			status = 'Successful'
			user.permission = trans_change_data['permission']
			user.email = trans_change_data['email']
			user.groups = trans_change_data['groups']
			user.save()
		else:
			status = 'Failed'

		rsp_data = {'status': status}
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
		if UserInfo.objects.filter(name = trans_add_data['name']):
			status = 'Failed'
		else:
			add_user = UserInfo(name = trans_add_data['name'], permission = trans_add_data['permission'])
			add_user.save()
			status = 'Successful'

		rsp_data = {'status': status}
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
		user_name = request.POST.getlist('req_json')[0]
		user_name = user_name.encode('utf-8')
		print 'user_name:   ', user_name
		user = UserInfo.objects.filter(name = user_name)[0]
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



class HandleFileAjaxFunc(object):
	def upload_file(self, request):
		rsp_data = {}
		if request.method == 'POST':
			start_time = int(time.time())
			upload_file = request.FILES['file']
			if upload_file:
				filename = str(upload_file).encode('utf-8')

				self.handle_uploaded_file(upload_file, filename)

				# filepath = os.path.join(cfg.WORK_PATH_TEMP, filename)
				# filedst = filepath + cfg.DOT + cfg.PID
				# destination = open(filepath,'wb+')
				# for chunk in upload_file.chunks():
				# 	destination.write(chunk)
				# destination.close()
				# status = 'Successful'
				# sock = sock_conn(ENV_KEY)
				# rtn = uploadFile(sock, filepath, filedst)
				# end_time = int(time.time())
				# upload_time = str(end_time - start_time)
				# print 'rtn: ', rtn
				# if rtn == cfg.CMD_SUCC:
				# 	rsp = recv_end(sock)
				# 	info = '<br/>File transfer SUCC, cost ' + str(end_time - start_time) + ' secs.'
				# 	status = "Successful"
				# else:
				# 	info = '<br/>File transfer FAIL, cost ' + str(end_time - start_time) + ' secs.'
				# 	status = 'Failed'
				# rsp = rsp + info
				# print rsp
				# print 'status: ', status
				# sock.close()

				rsp_data = {
					'type': 'Successful',
					'upload_time': 1
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
		with open(full_file_name, 'wb+') as destination:
			for chunk in file.chunks():
				destination.write(chunk)
		destination.close()		

class TaskAjaxFunc(object):
	@csrf_exempt
	def test_task_rpc(self, request):
		rsp_data = {'data': 'test_task_rpc!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def test_task_ntf(self, request):
		rsp_data = {'data': 'test_task_ntf!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def test_all_srvstatus(self, request):
		rsp_data = {'data': 'test_all_srvstatus!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def test_all_tasklist(self, request):
		rsp_data = {'data': 'test_all_tasklist!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def test_all_taskresult(self, request):
		rsp_data = {'data': 'test_all_taskresult!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response

	def test_all_version(self, request):
		rsp_data = {'data': 'test_all_version!'}
		response = HttpResponse(json.dumps(rsp_data))
		response["Access-Control-Allow-Origin"] = "*"
		response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
		response["Access-Control-Max-Age"] = "1000"
		response["Access-Control-Allow-Headers"] = "*"
		return response	

class AjaxReqFunc(AdminDataAjaxFunc, HandleFileAjaxFunc, TaskAjaxFunc):
	def __init__ (self):
		self.name = 'AjaxReqFunc'

	def default_ajax_request(self, request):
		return HttpResponse(json.dumps({'data':'AJAX Request Failed!'}), content_type = "application/json")

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
		group_array = []
		group_obj = GroupInfo.objects.all()
		for tmp_obj in group_obj:
			group_array.append(Group(tmp_obj.name, tmp_obj.permission).__dict__)
		tmp_object = {
			'user': g_login_user,
			'groups': group_array,
			'group_numbs': len(group_array)
		}
		return tmp_object

	def get_admin_auth_group_add_object(self):
		tmp_object = {
			'user': g_login_user
		}
		return tmp_object

	def get_admin_auth_group_change_object(self, cur_id = -1):
		group_json = {}
		if cur_id !=-1:
			group = GroupInfo.objects.filter(id = int(cur_id))[0]
			permission_array = []
			if group.permission == 'all':
				permission_array = g_group_permission
			else:
				permission_array = group.permission.split(';')
				permission_array.remove('')

			group_json = {
				'name': group.name
			}
		tmp_object = {
			'login_user': g_login_user,
			'group': group_json,
			'permission': permission_array
		}
		return tmp_object

	def get_admin_auth_user_object(self):
		user_array = []
		user_obj = UserInfo.objects.all()
		for tmp_obj in user_obj:
			user_array.append(User(tmp_obj.name, tmp_obj.email, \
			                  tmp_obj.permission, tmp_obj.groups).__dict__)
		tmp_object = {
			'user': g_login_user,
			'users': user_array,
			'user_numb': len(user_array)
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

			if user.permission == 'all':
				permission_array = g_group_permission
			else:
				permission_array = user.permission.split(';')
				permission_array.remove('')

			if user.groups == 'all':
				user_groups = available_groups
			else:
				user_groups = user.groups.split(';')
				user_groups.remove('')

			user_json = {
				'name': user.name,
				'email': user.email
			}
		tmp_object = {
			'login_user': g_login_user,
			'user': user_json,
			'permission': permission_array,
			'available_groups': available_groups,
			'user_groups': user_groups
		}
		return tmp_object

server_view = ViewMain()
