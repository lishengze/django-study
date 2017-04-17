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
def test_task_rpc(request):
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

def test_all_srvstatus(request):
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

def test_all_tasklist(request):
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

def test_all_taskresult(request):
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

def test_all_version(request):
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

def set_chosen_grouporuser(request):
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

def set_env_key(request):
	global ENV_KEY
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

def get_login_object():
	req_object = {
		'ENV_KEY': g_env_array
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
		'login_user': g_login_user,
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
		'login_user': g_login_user,
		'chosen_user': g_chosen_user
	}
	return tmp_object
