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
import types

console_path = cfg_w.CONSOLE_WORK_PATH
if console_path not in sys.path:
	sys.path.append(console_path)

import config as cfg
from ecall import *
from verControl import *
from taskinfo import *

import json

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
