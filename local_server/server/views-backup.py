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

def get_ajax_func(path):
	ajax_name = get_ajax_request_name(path)
	print 'ajax_name: ' + ajax_name
	ajax_func_dict = {
		'Request_All_SrvStatus': test_all_srvstatus,
		'Request_All_TaskList': test_all_tasklist,
		'Request_All_TaskResult': test_all_taskresult,
		'Request_All_Version': test_all_version,
        'Request_Task_Rpc': test_task_rpc,
        'Request_Task_Ntf': test_task_ntf
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

def get_test_req_object():
	req_object = {
		'name': 'Django',
		'user': g_login_user,
		'users': g_users
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
