#coding=utf-8

import os
import sys
import socket
import datetime
import time

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
import shutil

console_path = cfg_w.CONSOLE_WORK_PATH
if console_path not in sys.path:
	sys.path.append(console_path)

import config as cfg
from ecall import *
from verControl import *
from taskinfo import *
from tools import md5sum

ENV_KEY = 'MYTEST_170'

#欢迎页
@csrf_protect
def index(request, pageNo=None, etype=None, keyword=None):
	try:
		#文章分页后的页数
		pgNo=int(pageNo)
	except:
		pgNo=1
	try:
		etype=int(etype)
	except:
		etype=None

	if etype:
		#查询该类别的文章，exclude表示not in或者!=
		datas=Essay.objects.all().filter(eType=etype).exclude(title='welcome')
	elif keyword:
		#根据关键字查询,title__contains表示Sql like %+keyword+%
		#Q对象表示Sql关键字OR查询
		#详细的介绍http://docs.djangoproject.com/en/1.0/topics/db/queries/#complex-lookups-with-q-objects
		datas=Essay.objects.all().get(Q(title__contains=keyword)|
									  Q(abstract__contains=keyword)).exclude(title='welcome')
	else:
		#查询所有文章
		datas=Essay.objects.all().exclude(title='welcome')
	#最近的5篇文章
	recentList=datas[:5]
	#数据分页
	paginator = Paginator(datas, 10)
	if pgNo==0:
		pgNo=1
	if pgNo>paginator.num_pages:
		pgNo=paginator.num_pages
	curPage=paginator.page(pgNo)
	#返回到mian.html模板页
	return render(request, 'main.html',{'csrfmiddlewaretoken': 'random string',
										   'page':curPage,
										   'essay_type':EssayType.objects.all(),
										   'pcount':paginator.num_pages,
										   'recent':recentList,
										   'archives':Archive.objects.all(),
										   'welcome':Essay.objects.filter(title='welcome')[0]}
										   	)

#文章详细信息
@csrf_protect
def essay_details(request,eid=None):
	#返回文章详细信息或者404页面
	essay=get_object_or_404(Essay,id=eid)
	recentList=Essay.objects.all()[:5]
	#新用户的Session
	if request.session.get('e'+str(eid),True):
		request.session['e'+str(eid)]=False
		#这里可以用一个timer实现，浏览次数保存在内存中，
		#timer定期将浏览次数提交到数据库
		#文章浏览次数+1
		essay.view_count=essay.view_count+1
		essay.save()
	return render(request, 'details.html',{'csrfmiddlewaretoken': 'random string',
												  'essay':essay,
												  'essay_type':EssayType.objects.all(),
												   'archives':Archive.objects.all(),
												  'date_format':essay.pub_date.strftime('%A %B %d %Y').split(),
												  'recent':recentList
												  })
def leave_comment1(request,eid=None):
	if request.method == 'POST' and eid:
		uname=request.POST.get('uname',None)
		content=request.POST.get('comment',None)
		email=request.POST.get('email',None)
		essay=Essay.objects.get(id=eid)
		Dic_Run = {}
		Dic_Run[cfg.CMD] = 'deployConsole'
		Dic_Run[cfg.CTR] = 'PD'
		return HttpResponse(Ecall(**Dic_Run))
	return HttpResponse(cfg.SYS_WINDOWS)

def sock_conn(key):
	daemaon_ip = cfg_w.ENV_DICT[key][1]
	daemon_port = cfg_w.ENV_DICT[key][2]
	print(daemaon_ip, daemon_port)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((daemaon_ip, daemon_port))
	return sock

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
def update_srv(request):
	rsp = ''
	if request.method == "POST":
		start_time = int(time.time())
		myFile = request.FILES.get("myfile", None)	
		if not myFile:
			return HttpResponse("no files for upload!")
		filepath = os.path.join(cfg.WORK_PATH_TEMP, myFile.name)
		filedst = os.path.join(cfg.WORK_PATH_UPDATE, myFile.name)
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

@csrf_protect
def upload_file(request):
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

@csrf_protect
###执行即时任务
def download_file(request):
	#if request.method == 'POST':
	if request.method != '':

		#从POST请求中获取查询关键字
		FileName = request.POST.get('filename',None)
		if not FileName:
			return HttpResponse("no files for request!")
		sock = sock_conn(ENV_KEY)
		FileSrc = FileName
		FileDst = os.path.join(cfg.WORK_PATH_TEMP, FileName)
		FileNew = FileDst + cfg.DOT +cfg.PID
		FileNewDst = os.path.join(cfg.WORK_PATH_CFG, FileName + cfg.DOT + cfg.PID)
		rtn = downloadFile(sock, FileSrc, FileDst)
		sock.close()
		if rtn == cfg.CMD_SUCC:
			sock = sock_conn(ENV_KEY)
			shutil.copyfile(FileDst, FileNew)
			f = open(FileNew, "a+")
			f.write("## Add Test Info by " + str(cfg.PID) + ' \n')
			f.close()
			uploadFile(sock, FileNew, FileNewDst)
			result_info = " SUCC"
			sock.close()
		else:
			result_info = " FAILED"
			
		return HttpResponse("Download " + FileName + result_info)
	else:
		return index(request)

@csrf_protect
def readFile(request):
	"""
	根据web页面给定的文件名，读取服务器中文件的内容，并返回给页面
	"""
	if request.method != '':
		#从POST请求中获取查询关键字
		FileName = request.POST.get('filename',None)
		if not FileName:
			return HttpResponse("no files for request!")
		sock = sock_conn(ENV_KEY)
		FileSrc = FileName
		###1.根据文件名找到所需文件的路径(给定对象以及文件名)
		###！！！
		sock.send(genFReqHead(FileSrc) + cfg.TIP_INFO_EOF)
		rsp = recv_end(sock)
		###2.将找到的文件内容返回给django
		head_info, buf = getFRspHead(rsp)
		sock.close()
		return HttpResponse(buf.replace("\n", "<br/>"))
	else:
		return index(request)

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
			sock = sock_conn(ENV_KEY)
			sock.send(genRpcHead() + task_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
			sock.close()
		except Exception as e:
			print('notifyDaemon failed!')
			print((traceback.format_exc()))
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
			sock = sock_conn(ENV_KEY)
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
			sock = sock_conn(ENV_KEY)
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
			sock = sock_conn(ENV_KEY)
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

###查询所有计划任务
@csrf_protect
def query_all_task(request):
	#if request.method == 'POST':
	if request.method != '':
		#从POST请求中获取查询关键字
		req_info = ReqInfo(0, cfg.FLAG_REQTYPE_TASKMAP)
		rsp = ''
		try:
			sock = sock_conn(ENV_KEY)
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
			sock = sock_conn(ENV_KEY)
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
			sock = sock_conn(ENV_KEY)
			sock.send(genReqHead() + req_info.encode() + cfg.TIP_INFO_EOF)
			rsp = recv_end(sock)
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
				print(info.encode())
		except Exception as e:
			print('notifyDaemon failed!')
			print(traceback.format_exc())
		return HttpResponse(rsp.replace("\n", "<br/>"))
	else:
		return index(request)
#根据关键字来搜索文章
def search(request):
	if request.method == 'POST':
		#从POST请求中获取查询关键字
		key=request.POST.get('keyword',None)
		print(task_info.encode())
		return index(request,keyword=key)
	else:
		return index(request)


#存储用户留言信息
def leave_comment(request,eid=None):
	if request.method == 'POST' and eid:
		uname=request.POST.get('uname',None)
		content=request.POST.get('comment',None)
		email=request.POST.get('email',None)
		essay=Essay.objects.get(id=eid)
		if uname and content and email and essay:
			comment=Comment()
			comment.uname=uname
			comment.content=content
			comment.email=email
			comment.essay=essay
			comment.pub_date=datetime.datetime.now()
			comment.save()
			return essay_details(request,eid)
		return index(request)

	return index(request)

@csrf_protect
def alogin(request):
	errors= []
	account=None
	password=None
	if request.method == 'POST' :
		if not request.POST.get('account'):
			errors.append('Please Enter account')
		else:
			account = request.POST.get('account')
		if not request.POST.get('password'):
			errors.append('Please Enter password')
		else:
			password= request.POST.get('password')
		if account is not None and password is not None :
			user = auth.authenticate(username=account, password=password)
			if user is not None:
				if user.is_active:
					auth.login(request, user)
					return HttpResponseRedirect('/')
				else:
					errors.append('disabled account')
			else :
				errors.append('invaild user')
	return render(request, 'login.html', {'csrfmiddlewaretoken': 'random string', 'errors': errors})

@csrf_protect
def register(request):
	errors= []
	account=None
	password=None
	password2=None
	email=None
	CompareFlag=False

	if request.method == 'POST':
		if not request.POST.get('account'):
			errors.append('Please Enter account')
		else:
			account = request.POST.get('account')
		if not request.POST.get('password'):
			errors.append('Please Enter password')
		else:
			password = request.POST.get('password')
		if not request.POST.get('password2'):
			errors.append('Please Enter password2')
		else:
			password2 = request.POST.get('password2')
		if not request.POST.get('email'):
			errors.append('Please Enter email')
		else:
			email= request.POST.get('email')

		if password is not None and password2 is not None:
			if password == password2:
				CompareFlag = True
			else :
				errors.append('password2 is diff password ')


		if account is not None and password is not None and password2 is not None and email is not None and CompareFlag:
			userlist = User.objects.all()
			try:
				user=User.objects.create_user(account, email, password)
			except IntegrityError as e:
				return HttpResponse(e)
			else:
				user.is_active=True
				user.save
				return HttpResponseRedirect('/account/login/')

	return render(request, 'register.html', {'csrfmiddlewaretoken': 'random string', 'errors': errors})

def alogout(request):
	auth.logout(request)
	return HttpResponseRedirect('/')