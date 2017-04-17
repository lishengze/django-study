#!/usr/bin/python
#	-*-	coding:	utf-8	-*-
"""
:copyright: (c) 2016 by chen.xh.
:license:BSD.
"""

import time
import socket

import config as cfg

def recv_end(the_socket):
	"""
	定义socket接受字节数
	Args：
		sock连接
	Returns:
		返回从sock连接中接收到的字节，在config.py中定义为8192
	"""
	total_data = []
	data = cfg.FLAG_NULL
	while True:
		data = the_socket.recv(cfg.DEFAULT_RECV)
		if cfg.TIP_INFO_EOF in data:
			total_data.append(data[:data.find(cfg.TIP_INFO_EOF)])
			break
		total_data.append(data)
		if len(total_data) > 1:
			#check if end_of_data was split
			last_pair = total_data[-2] + total_data[-1]
			if cfg.TIP_INFO_EOF in last_pair:
				total_data[-2]=last_pair[:last_pair.find(cfg.TIP_INFO_EOF)]
				total_data.pop()
				break
	return cfg.FLAG_NULL.join(total_data)

def getInfo(buf, tip_start, tip_end):
	"""
	从socket接收的数据中解析出标记中的信息
	Args:
		buf: socket.recv()
		tip_start:开始标记
		tip_end:结束标记
		
	Returns:
		info：开始标记及结束标记之间的内容
		buf:结束标记后面的内容
	"""
	info = cfg.FLAG_NULL
	start_pos = buf.find(tip_start)
	if start_pos != -1:
		end_pos = buf.find(tip_end, start_pos)
		if end_pos != -1:
			info = buf[start_pos+len(tip_start):end_pos].strip()
			start_pos_new = end_pos + len(tip_end)
			if start_pos_new < len(buf):
				buf = buf[start_pos_new:]
			else:
				buf = cfg.FLAG_NULL
	return info, buf

def getTaskInfo(buf):
	"""
	获取[TASK]标记后面的内容，即任务信息
	Args:
		sock接收的内容
	Returns:
		Task_Info对象
	"""
	return getInfo(buf, cfg.TIP_INFO_TASK, cfg.NEWLINE)

def getReqInfo(buf):
	"""
	获取[REQ]标记后面的内容，即请求信息
	"""
	return getInfo(buf, cfg.TIP_BODY_REQ, cfg.NEWLINE)

def getHeadInfo(buf):
	"""
	获取[HEAD]标记后面的内容
	"""
	return getInfo(buf, cfg.TIP_HEAD, cfg.NEWLINE)

def getTaskResult(task_info, buf):
	"""
	获取'[RESULT]<<<' '[RESULT]>>>'之间的内容，即task_info执行命令的结果
	"""
	return getInfo(buf, cfg.TIP_RESULT_START, cfg.TIP_RESULT_END)

def genSeqId():
	return int(time.time()) * 100000 + int(cfg.PID)

def getSeqId(info, tip):
	seqId = 0
	tip_pos =  info.find(tip)
	if tip_pos != -1:
		seqId = int(info[tip_pos+len(tip):])
	return seqId

def genReqHead():
	return cfg.TIP_HEAD + cfg.TIP_HEAD_REQ + str(genSeqId()) + cfg.NEWLINE

def genRpcHead():
	return cfg.TIP_HEAD + cfg.TIP_HEAD_RPC + str(genSeqId()) + cfg.NEWLINE

def genNtfHead():
	return cfg.TIP_HEAD + cfg.TIP_HEAD_NTF + str(genSeqId()) + cfg.NEWLINE

def genRspHead(req_id):
	return cfg.TIP_HEAD + cfg.TIP_HEAD_RSP + str(req_id) + cfg.NEWLINE

class ReqInfo:
	"""
	请求信息
	"""
	def __init__(self, TID=0, req_type=cfg.FLAG_REQTYPE_TASKINFO):
		self.TID = TID
		self.req_type = req_type

	def encode(self):
		info_str = cfg.TIP_BODY_REQ + str(self.TID) + cfg.DCOLON + str(self.req_type) + cfg.NEWLINE
		return info_str

	def decode(self, info_str):
		info_list = info_str.split(cfg.DCOLON)
		if len(info_list) == 2:
			self.TID = int(info_list[0])
			self.req_type = int(info_list[1])
			return True
		else:
			return False

class TaskInfo:
	"""
	任务信息
	"""
	def __init__(self, TID=0, state=0, PID=0, exec_time=0, cmd=cfg.FLAG_NULL, cmdline=cfg.FLAG_NULL, task_type=0):
		self.info_time = int(time.time())
		self.exec_time = exec_time
		self.state = state
		self.PID = PID
		self.TID = TID if (TID > 0) else self.info_time * 100000 + self.PID
		self.cmd = cmd
		self.cmdline = cmdline
		self.task_type = task_type

	def setState(self, state):
		self.state = state
		self.info_time = int(time.time())

	def setExecTime(self, exec_time=0):
		self.exec_time = exec_time

	def encode(self):
		info_str = cfg.TIP_INFO_TASK + str(self.TID) + cfg.DCOLON + str(self.state) \
			+ cfg.DCOLON + str(self.info_time) + cfg.DCOLON + str(self.exec_time) + cfg.DCOLON + str(self.PID) \
			+ cfg.DCOLON + self.cmd + cfg.DCOLON + self.cmdline + cfg.DCOLON + str(self.task_type) + cfg.NEWLINE
		return info_str

	def decode(self, info_str):
		info_list = info_str.split(cfg.DCOLON)
		if len(info_list) == 8:
			self.TID = int(info_list[0])
			self.state = int(info_list[1])
			self.info_time = int(info_list[2])
			self.exec_time = int(info_list[3])
			self.PID = info_list[4]
			self.cmd = info_list[5]
			self.cmdline = info_list[6]
			self.task_type = int(info_list[7])
			return True
		else:
			return False

	def shouldExec(self, timestamp):
		if timestamp >= self.exec_time and (not isTimeOut(timestamp)):
			return True
		else:
			return False

	def isTimeOut(self, timestamp=int(time.time())):
		if timestamp - self.exec_time > cfg.TIMEOUT_SCHDL_TASK:
			return True
		else:
			return False

class SrvStatus:
	def __init__(self, srvid=cfg.FLAG_NULL, status=cfg.FLAG_SRV_UNKNOWN, timestamp=int(time.time()), ip=cfg.FLAG_NULL, cmdline=cfg.FLAG_NULL, PID=0, starttime=cfg.FLAG_NULL):
		self.srvid = srvid
		self.status = status
		self.timestamp = timestamp
		self.ip = ip
		self.cmdline = cmdline
		self.PID = PID
		self.starttime = starttime

	def setStatus(self, status, timestamp):
		self.status = status
		self.timestamp = timestamp

	def setInfo(self, srvid, ip, cmdline, PID=0, starttime=cfg.FLAG_NULL):
		self.srvid = srvid
		self.PID = PID
		self.ip = ip
		self.starttime = starttime
		self.cmdline = cmdline

	def isTimeOut(self, timestamp=int(time.time())):
		if timestamp - self.timestamp > cfg.TIMEOUT_SRV_STATUS:
			return True
		else:
			return False

	def encode(self):
		info_str = cfg.TIP_BODY_REQ + str(self.srvid) + cfg.DCOLON + str(self.status) + cfg.DCOLON + str(self.timestamp)\
			+ cfg.DCOLON + str(self.ip) + cfg.DCOLON + str(self.cmdline) + cfg.DCOLON + str(self.PID)\
			+ cfg.DCOLON + str(self.starttime) + cfg.NEWLINE
		return info_str

	def decode(self, info_str):
		info_list = info_str.split(cfg.DCOLON)
		if len(info_list) == 7:
			self.srvid = info_list[0]
			self.status = info_list[1]
			self.timestamp = int(info_list[2])
			self.ip = info_list[3]
			self.cmdline = info_list[4]
			self.PID = int(info_list[5])
			self.starttime = info_list[6]
			return True
		else:
			return False

	def toString(self):
		return "%s %d %d %s %s %s %d"%(self.srvid, self.status, self.PID, self.ip, self.starttime, self.cmdline, self.timestamp)

class VersionInfo:
	def __init__(self, object='server', version='0.0.0', datetime='0', status='-'):
		self.object = object
		self.version = version
		self.datetime = datetime
		self.status = status
	
	def encode(self):
		info_str = cfg.TIP_BODY_VERINFO + str(self.object) + cfg.DCOLON + str(self.version) + cfg.DCOLON + str(self.datetime)\
			+ cfg.DCOLON + str(self.status) + cfg.NEWLINE
		return info_str

	def decode(self, info_str):
		info_list = info_str.split(cfg.DCOLON)
		if len(info_list) == 4:
			self.object = info_list[0]
			self.version = info_list[1]
			self.datetime = info_list[2]
			self.status = info_list[3]
			return True
		else:
			return False	
'''
from taskinfo import TaskInfo

testTask = TaskInfo(state=2, PPID=112, PID=1111, cmd='publish', cmdline='--cmd publish --ctr PD')
print(testTask.encode())
print(testTask.decode('148888847400112::2::1488888474::1234::5678::pub::--cmd pub --ctr PD --srv sysagent'))
print(testTask.encode())
'''
