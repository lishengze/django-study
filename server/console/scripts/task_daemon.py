#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Process mutex lock.
Actually it is implemented by file lock.
:copyright: (c) 2016 by chen.xh.
:license:BSD.
"""

import sys, os, time, atexit
import socket
import traceback
import threading
from multiprocessing import Process, Manager
from signal import SIGTERM

import config as cfg
from taskinfo import recv_end, getTaskInfo, getReqInfo, getHeadInfo, getTaskResult, getSeqId, \
	genRpcHead, genRspHead, ReqInfo, TaskInfo, SrvStatus, VersionInfo
from tools import loadPickle, dumpPickle, loadVersionMap

taskmap = {}			## 用于保存各任务信息{TaskID:TaskInfo}
task_reuslt_map = {}	## 用于保存已结束任务的结果信息{TaskID:TaskResults}
TaskList = []			## 用于保存计划任务的列表
srv_status_map = {}		## 用于保存服务状态的map{SrvID:SrvStatus}

class Daemon:
	"""
	守护进程父进程
	"""
	def __init__(self, pidfile, subpidfile, stderr=cfg.FILE_DAEMON_ERR, stdout=cfg.FILE_DAEMON_OUT, stdin=cfg.FILE_DAEMON_IN):
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
		self.pidfile = pidfile
		self.subpidfile = subpidfile
		self.pid = 0

	def dumppid(self, pidfile, pid):
		"""
		生成守护进程的pidfiles
		"""
		if cfg.FLAG_DEBUG:
			print("Dump pidfile [%s] [%s]"%(pidfile, pid))
		file(pidfile,'w+').write("%s\n" % pid)

	def _daemonize(self):
		#脱离父进程
		try:
			pid = os.fork()
			if pid > 0:
				sys.exit(0)
		except OSError, e:
			sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)

		#脱离终端
		os.setsid()
		#修改当前工作目录
		os.chdir("/")
		#重设文件创建权限
		os.umask(0)

		#第二次fork，禁止进程重新打开控制终端
		try:
			pid = os.fork()
			if pid > 0:
				sys.exit(0)
		except OSError, e:
			sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)
		try:
			if cfg.FLAG_DEBUG:
				print('Daemon pid [%s] start'%(str(os.getpid())))
			sys.stdout.flush()
			sys.stderr.flush()
			si = file(self.stdin, 'r')
			so = file(self.stdout, 'w+')
			se = file(self.stderr, 'w+', 0)
			#重定向标准输入/输出/错误
			os.dup2(si.fileno(), sys.stdin.fileno())
			os.dup2(so.fileno(), sys.stdout.fileno())
			os.dup2(se.fileno(), sys.stderr.fileno())

			#注册程序退出时的函数，即删掉pid文件
			atexit.register(self.delpid)
			self.pid = str(os.getpid())
			self.dumppid(self.pidfile, self.pid)
			print('Daemon pid [%s] start'%(self.pid))
		except Exception:
			sys.stderr.write(traceback.format_exc())
			sys.exit(1)

	def delpid(self):
		"""
		删除pid文件
		"""
		if self.pid == str(os.getpid()):
			if cfg.FLAG_DEBUG:
				print('daemon process exit! del pidfile!')
			if os.path.exists(self.pidfile):
				os.remove(self.pidfile)
			if os.path.exists(self.subpidfile):
				os.remove(self.subpidfile)
		else:
			print('son process exit!')

	def start(self):
		"""
		Start the daemon
		"""
		# Check for a pidfile to see if the daemon already runs
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None

		if pid:
			if cfg.FLAG_DEBUG:
				print('Daemon pid [%d] run'%(pid))
				message = "pidfile %s already exist. Daemon already running?\n"
				sys.stderr.write(message % self.pidfile)
			sys.exit(1)

		# Start the daemon
		self._daemonize()
		self._run()

	def stop(self):
		# Get the pid from the pidfile
		try:
			pid = None
			subpid = None
			if os.path.exists(self.pidfile):
				pf = file(self.pidfile,'r')
				pid = int(pf.read().strip())
				pf.close()
			if os.path.exists(self.subpidfile):
				subpf = file(self.subpidfile,'r')
				subpid = int(subpf.read().strip())
				subpf.close()
			if cfg.FLAG_DEBUG:
				print('Daemon pid [%d] stop'%(pid))

		except IOError:
			pid = None

		if not pid:
			message = "pidfile %s does not exist. Daemon not running?\n"
			if cfg.FLAG_DEBUG:
				print(message % self.pidfile)
			return # not an error in a restart
		# Try killing the daemon process
		try:
			while 1:
				if subpid > 0:
					os.kill(subpid, SIGTERM)
				if pid > 0:
					os.kill(pid, SIGTERM)
				time.sleep(0.1)
		except OSError, err:
			err = str(err)
			if err.find("No such process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
			else:
				print str(err)
				sys.exit(1)

	def restart(self):
		self.stop()
		self.start()

	def _run(self):
		pass

def doTask(task_info):
	"""
	执行task，调用main.py或verControl.py执行页面请求的指令
	Args:
		task_info:Task_info 对象
	"""
	try:
		result = cfg.FLAG_NULL
		pid = os.getpid()
		startTime = time.time()
		if cfg.FLAG_DEBUG:
			print("process[%d] doTask start at %s"%(pid, startTime))
		if task_info.task_type == cfg.TASK_TYPE_ECALL:
			cmdline = "python %s --tid %d %s"%(cfg.FILE_NAME_MAIN, task_info.TID, task_info.cmdline)
		elif task_info.task_type == cfg.TASK_TYPE_VERCONTROL:
			#cmdline = "python %s --tid %d %s"%(cfg.FILE_NAME_VERCTRL, task_info.TID, task_info.cmdline)
			cmdline = "python %s %s"%(cfg.FILE_NAME_VERCTRL, task_info.cmdline)	
		if cfg.FLAG_DEBUG:
			print("cmdline[%s]"%(cmdline))
		os.chdir(cfg.WORK_PATH_SCR)
		result = os.popen(cmdline,'r').read()
		print(result)
		endTime = time.time()
		if task_info.cmd in cfg.CMDS_APP_BASE:
			#updateSrvStatusFromDoTask(result)
			showSrvStatus()
		else:
			print('tastInfo cmd is [%s]'%(task_info.cmd))

		with open(cfg.FILE_DAEMON_TASKOUT, 'a') as f:
			info = "===== process[%d] doTask [%s] start at [%s]\n"%(pid, task_info.cmdline, startTime) \
				+ result + "----- process[%d] doTask [%s]  end  at [%s]\n"%(pid, task_info.cmdline, endTime)
			f.write(info)
			
		if cfg.FLAG_DEBUG:
			print("process[%d] doTask  end  at %s"%(pid, endTime))
			print("doTask cost time [%d] secs"%(int(endTime) - int(startTime)))
	except Exception, e:
		print((traceback.format_exc()))
	finally:
		return result

def updateTaskStatus(task_info):
	"""
	更新task_info
	"""
	taskmap[task_info.TID] = task_info
	showTaskStatus()

def showTaskStatus():
	"""
	查看任务列表的状态，（ready or start or end）
	"""
	start_num = 0
	ready_num = 0
	end_num = 0
	if cfg.FLAG_DEBUG:
		print('-------------------------------Task list---------------------------------')
	iCount = 0
	task_keys = sorted(taskmap.keys())
	for tid in task_keys:
		iCount += 1
		if cfg.FLAG_DEBUG:
			print('[%d] %d [%d] %s\n'%(iCount, tid, taskmap[tid].state, taskmap[tid].cmdline))
		if taskmap[tid].state == cfg.FLAG_TASK_READY:
			ready_num += 1
		elif taskmap[tid].state == cfg.FLAG_TASK_START:
			start_num += 1
		elif taskmap[tid].state == cfg.FLAG_TASK_END:
			end_num += 1
	###!!!
	status = "Total [%d] tasks, R/S/E = [%d/%d/%d]"%( len(taskmap),ready_num, start_num, end_num)
	if cfg.FLAG_DEBUG:
		print('-------------------------------------------------------------------------')
		print(status)
		print('')
	return status

def showSrvStatus():
	"""
	查看服务状态
	"""
	alive_num = 0
	notalive_num = 0
	undeploy_num = 0
	unknown_num = 0
	if cfg.FLAG_DEBUG:
		print('-------------------------------Srv list---------------------------------')
	iCount = 0
	srv_keys = sorted(srv_status_map.keys())
	for srvid in srv_keys:
		iCount += 1
		if cfg.FLAG_DEBUG:
			print('[%d] %s\n'%(iCount, srv_status_map[srvid].toString()))
		if srv_status_map[srvid].status == cfg.FLAG_SRV_UNKNOWN:
			unknown_num += 1
		elif srv_status_map[srvid].status == cfg.FLAG_SRV_UNDEPLOY:
			undeploy_num += 1
		elif srv_status_map[srvid].status == cfg.FLAG_SRV_ALIVE:
			alive_num += 1
		elif srv_status_map[srvid].status == cfg.FLAG_SRV_NOTALIVE:
			notalive_num += 1
	###!!!
	status = "Total [%d] SRVs, UN/UD/R/S = [%d/%d/%d/%d]"%( len(srv_status_map),unknown_num, undeploy_num, alive_num, notalive_num)
	if cfg.FLAG_DEBUG:
		print('-------------------------------------------------------------------------')
		print(status)
		print('')
	return status

def genRspBody(req_info):
	"""
	根据req_info的请求对象，提供请求任务信息后任务结果信息
	Args:
		req_info:ReqInfo的实例
	"""
	try:
		TID = req_info.TID
		#请求类型为查看任务列表
		if req_info.req_type == cfg.FLAG_REQTYPE_TASKINFO:
			task_info_str = cfg.FLAG_NULL
			if TID == 0 :
				## Get all taskinfo
				task_keys = sorted(taskmap.keys())
				for tid in task_keys:
					task_info_str += taskmap[tid].encode()
			else:
				if taskmap.get(TID):
					task_info_str = taskmap[TID].encode()
				else:
					print("get [%d] failed!"%(TID))
				## Get one taskinfo
			return task_info_str
		#请求类型为查看任务列表对应的结果
		elif req_info.req_type == cfg.FLAG_REQTYPE_TASKRESULT:
			task_result_str = cfg.FLAG_NULL
			if TID == 0:
				## Get all taskinfo
				task_keys = sorted(task_reuslt_map.keys())
				for tid in task_keys:
					task_result_str += task_reuslt_map[tid]
			else:
				if task_reuslt_map.get(TID):
					task_result_str = task_reuslt_map[TID]
				else:
					print("get [%d] failed!"%(TID))
			return task_result_str
		#请求类型为查看计划任务列表
		elif req_info.req_type == cfg.FLAG_REQTYPE_TASKLIST:
			task_info_str = cfg.FLAG_NULL
			for task_info in TaskList:
				task_info_str += task_info.encode()
			return task_info_str
		
		elif req_info.req_type == cfg.FLAG_REQTYPE_VERSION:
			ver_info_str = cfg.FLAG_NULL
			ver_map = loadVersionMap()
			
			if TID == 0 or TID > 3:
				for object in ver_map.keys():
					ver_list = ver_map[object]
					for ver_item in ver_list[1:]:
						version = ver_item[0]
						datetime = ver_item[1]
						status = ver_item[2]
						ver_info = VersionInfo(object, version, datetime, status)
						ver_info_str += ver_info.encode()
				return ver_info_str
			else:
				if TID == 1:
					object = "client"
				elif TID == 2:
					object = "server"
				elif TID == 3:
					object = "xml"
				ver_list = ver_map[object]
				for ver_item in ver_list[1:]:
					version = ver_item[0]
					datetime = ver_item[1]
					status = ver_item[2]
					ver_info = VersionInfo(object, version, datetime, status)
					ver_info_str += ver_info.encode()
				return ver_info_str
		#请求类型为查看服务运行状态
		elif req_info.req_type == cfg.FLAG_REQTYPE_SRVSTATUS:
			print('**********************************************')
			print("FLAG_REQTYPE_SRVSTATUS:%d"%(req_info.req_type))
			srv_status_str = cfg.FLAG_NULL
			srv_keys = sorted(srv_status_map.keys())
			for srvid in srv_keys:
				srv_status_str += srv_status_map[srvid].encode()
			return srv_status_str
		else:
			pass
	except Exception, e:
		print((traceback.format_exc()))
		raise e

def setSrvStatus(srvid, status, timestamp):
	"""
	设置SrvStatus对象的状态属性
	"""
	if srv_status_map.get(srvid):
		srv_status_map[srvid].setStatus(status, timestamp)
	else:
		srv_status = SrvStatus(srvid, status, timestamp)
		srv_status_map[srvid] = srv_status
	print("SET:%s %d %d"%(srvid, status, timestamp))
	print("LEN(srv_status_map):[%d]"%(len(srv_status_map)))

def setSrvInfo(srvid, ip, cmdline, PID=0, starttime=cfg.FLAG_NULL):
	if srv_status_map.get(srvid):
		srv_status_map[srvid].setInfo(srvid, ip, cmdline, PID, starttime)
	else:
		srv_status = SrvStatus()
		srv_status.setInfo(srvid, ip, cmdline, PID, starttime)
		srv_status_map[srvid] = srv_status

def updateSrvStatusFromDoTask(result_info):
	"""
	针对指令"start, stop, show, alive"，根据ecall脚本的执行结果，更新SrvStatus对象的状态
	"""
	timestamp = int(time.time())
	result_info.replace('\r', cfg.FLAG_NULL)
	for line in result_info.split('\n'):
		if line.strip().startswith(cfg.OPEN_BRACKET):
			print('LINE:' + line)
			left = line.rfind(cfg.OPEN_BRACKET)
			right = line.find(cfg.CLOSE_BRACKET, left)
			if left != -1 and right != -1:
				srvid = line[left+1:right].strip()
				if len(line) > right + 1:
					status = line[right+1:].strip()
					print("SRV[%s] STATUS[%s]"%(srvid, status))
					if status == cfg.CMD_FAIL_TIP:
						setSrvStatus(srvid, cfg.FLAG_SRV_UNKNOWN, timestamp)
	showSrvStatus()

def updateSrvStatusFromNTF(result_info):
	"""
	针对指令"start, stop, show, alive"，根据前台网页的通知信息以及appctl.sh脚本的结果，更新SrvStatus对象的状态
	"""
	result_info.replace('\r', cfg.FLAG_NULL)
	timestamp = int(time.time())
	for line in result_info.split('\n'):
		line_list = line.strip().split(cfg.DCOLON)
		if len(line_list) >= 4:
			ip = line_list[1]
			srvid = line_list[2]
			status = line_list[3]
			status_list = status.strip().split()

			if status == cfg.CMD_UNDEPLOY_TIP:
				setSrvStatus(srvid, cfg.FLAG_SRV_UNDEPLOY, timestamp)
			elif status == cfg.CMD_CONNERR_TIP:
				setSrvStatus(srvid, cfg.FLAG_SRV_UNKNOWN, timestamp)	
			elif status in (cfg.CMD_NOALIVE_TIP, cfg.CMD_STOPPED_TIP):
				setSrvStatus(srvid, cfg.FLAG_SRV_NOTALIVE, timestamp)
			elif status == cfg.CMD_RUNNING_TIP:
				setSrvStatus(srvid, cfg.FLAG_SRV_ALIVE, timestamp)
			else:
				pid = int(status_list[0])
				starttime = status_list[1]
				cmdline = ' '.join(status_list[2:])
				setSrvInfo(srvid, ip, cmdline, pid, starttime)
				setSrvStatus(srvid, cfg.FLAG_SRV_ALIVE, timestamp)
	showSrvStatus()

def ScanTaskList():
	"""
	扫描任务列表，验证任务状态，并执行可执行的任务
	"""
	global TaskList
	iCount = 0
	while True:
		iCount += 1
		timestamp = int(time.time())
		if cfg.FLAG_DEBUG and iCount > 120:
			iCount = 0
			print("ScanTaskList at %d Length of TaskList is [%d]"%(timestamp, len(TaskList)))
		
		for task_info in TaskList:
			if task_info.isTimeOut(timestamp):
				print("[DROP] timeout task [%s] [%d] [%d]"%(task_info.cmdline, task_info.TID, task_info.exec_time))
				TaskList.remove(task_info)
				dumpPickle(TaskList, cfg.FILE_DAEMON_TASK_LIST)
			elif task_info.shouldExec(timestamp):
				sub_thread = threading.Thread(target=doTask, args=(task_info,))
				print("[START] ontime task [%s] [%d] [%d]"%(task_info.cmdline, task_info.TID, task_info.exec_time))
				sub_thread.start()
				TaskList.remove(task_info)
				dumpPickle(TaskList, cfg.FILE_DAEMON_TASK_LIST)
		time.sleep(0.5)

def ScanSrvStatusMap():
	"""
	查看服务状态Map，以剔除过期信息
	"""
	global srv_status_map
	timestamp = int(time.time())
	if cfg.FLAG_DEBUG:
		print("ScanSrvStatusMap at %d Length of SrvStatusMap is [%d]"%(timestamp, len(srv_status_map)))
	for srvid in srv_status_map.keys():
		srv_status = srv_status_map[srvid]
		if srv_status.isTimeOut(timestamp):
			print('del %s from srv_status_map'%(srv_status.tostring()))
			del srv_status_map[srvid]

def AddTask(task_info):
	"""
	添加Task_info对象到任务列表
	"""
	global TaskList
	print("before add %d"%(len(TaskList)))
	print(task_info)
	TaskList.append(task_info)
	dumpPickle(TaskList, cfg.FILE_DAEMON_TASK_LIST)		## 计划任务信息列表落地到文件，以应对进程重启
	print("after  add %d"%(len(TaskList)))

class MyDaemon(Daemon):
	"""
	守护进程
	"""
	def __init__(self, pidfile, subpidfile):
		Daemon.__init__(self,pidfile, subpidfile)

	def _run(self):
		"""
		1.Create Child to scan task_list
		2.
		"""
		try:
			print("srv_status_map")
			print(srv_status_map)
			if os.path.exists(cfg.FILE_DAEMON_TASK_LIST):
				TaskList = loadPickle(cfg.FILE_DAEMON_TASK_LIST)
			sub_thread_scantask = threading.Thread(target=ScanTaskList)
			sub_thread_scansrv = threading.Thread(target=ScanSrvStatusMap)
			sub_thread_scantask.start()		## 扫描计划任务列表，以开始到期任务
			sub_thread_scansrv.start()		## 扫描服务状态列表，以删除过期信息

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.bind((cfg.DAEMON_IP, cfg.DAEMON_PORT))
			s.listen(5)
			while 1:
				conn, addr = s.accept()
				if cfg.FLAG_DEBUG:
					print("Accept connection from ", conn.getpeername())
				buf = recv_end(conn)
				if buf:
					if cfg.FLAG_DEBUG:
						print('buf:[%s]'%(buf))
					head_info, buf = getHeadInfo(buf)
					if cfg.FLAG_DEBUG:
						print('get {%s}{%s} from getHeadInfo'%(head_info, buf))
					#信息请求指令
					if head_info.startswith(cfg.TIP_HEAD_REQ):
						req_info = ReqInfo()
						reqId = getSeqId(head_info, cfg.TIP_HEAD_REQ)
						info, buf = getReqInfo(buf)
						req_info.decode(info)
						if cfg.FLAG_DEBUG:
							print("ReqInfo:")
							print(req_info.TID, req_info.req_type)
						rsp_head = genRspHead(reqId)
						#rsp_status = showTaskStatus()
						rsp_body = genRspBody(req_info)
						if cfg.FLAG_DEBUG:
							print(rsp_head + rsp_body + cfg.TIP_INFO_EOF)
						conn.send(rsp_head + rsp_body + cfg.TIP_INFO_EOF)
					#通知任务状态变化（包括新建计划任务）
					elif head_info.startswith(cfg.TIP_HEAD_NTF):
						task_info = TaskInfo()
						info, buf = getTaskInfo(buf)
						if cfg.FLAG_DEBUG:
							print('get {%s}{%s} from getTaskInfo'%(info, buf))
						task_info.decode(info)
						updateTaskStatus(task_info)
						if task_info.state == cfg.FLAG_TASK_READY:
							AddTask(task_info)	## 添加计划任务
						elif task_info.state == cfg.FLAG_TASK_END:
							result_info, buf = getTaskResult(task_info, buf)
							if task_info.cmd in cfg.CMDS_APP_BASE:
								updateSrvStatusFromNTF(result_info)
							if cfg.FLAG_DEBUG:
								print('get {%s}{%s} from getTaskResult'%(result_info, buf))
							task_reuslt_map[task_info.TID] = result_info
					#发起远程方法调用
					elif head_info.startswith(cfg.TIP_HEAD_RPC):
						task_info = TaskInfo()
						info, buf = getTaskInfo(buf)
						print('get {%s}{%s} from getTaskInfo'%(info, buf))
						task_info.decode(info)
						result_info = doTask(task_info)  ## 执行即时任务并返回
						print('get {%s} from doTask'%(result_info))
						rpc_head = genRpcHead()
						#rsp_body = genRspBody(result_info)
						if cfg.FLAG_DEBUG:
							print(rpc_head + result_info + cfg.TIP_INFO_EOF)
						conn.send(rpc_head + result_info + cfg.TIP_INFO_EOF)
					else:
						print('Get invalid info_head[%s]'%(head_info))
				conn.close()
		except Exception, e:
			print(traceback.format_exc())
			raise e

if __name__ == "__main__":
	daemon = MyDaemon(cfg.FILE_DAEMON_MAINPID, cfg.FILE_DAEMON_SUBPID)
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			if cfg.FLAG_DEBUG:
				print 'start daemon'
			daemon.start()
		elif 'stop' == sys.argv[1]:
			if cfg.FLAG_DEBUG:
				print 'stop daemon'
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			if cfg.FLAG_DEBUG:
				print 'restart daemon'
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		print(srv_status_map)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
