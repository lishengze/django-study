#!/usr/bin/python
#	-*-	coding:	utf-8	-*-

"""
应用服务的版本管理相关
:copyright: (c) 2016 by chen.xh.
:license:BSD.
"""

import os
import sys
import re
import threading
import time
import traceback
import string
import tarfile
import shutil
import pickle
import Queue
import zipfile
import copy
import stat
import socket
import getopt

import config as cfg
from tools import logAttr, logEvent, md5check, doExit, zip_dir, unzip_file,\
	delFilepath, loadPickle, dumpPickle, getObjectPath
from getCfg import getcfg, loadHostMap, dumpHostMap, sortHostMap, loadRelayFile
from srvControl import updateSrv, deploySrv, undeploySrv
from threadpool import WorkRequest, ThreadPool
from ssh import ssh_conn, ssh_exec, ssh_opensftp, ssh_close, sftp_put, FLAG_SSH
from taskinfo import genNtfHead, TaskInfo

#g_iFinish = 0
#g_iTotal = 0
g_Lock = threading.Lock()

def Usage():
	print("Usage for ecall:")
	print("  python main.py --cmd CMD_OPTION [--grp GROUP] [--ctr CTR] [--srv SRV] [--srvno SRVNO] [--ictr CTR] [--isrv SRV] [--isrvno SRVNO]")
	print("")
	print("CMD_OPTION as:")
	print("  info [--args host|relay|app]  -- -- Show server apps infos")
	print("  deployConsole                 -- -- Deploy console toolkits")
	print("  undeployConsole               -- -- UnDeploy console toolkits")
	print("  deployServer                  -- -- Deploy server apps")
	print("  undeployServer                -- -- UnDeploy server apps")
	print("  copyXML                       -- -- Deploy xml-config for server")
	print("  show                          -- -- Show server apps infos")
	print("  alive                         -- -- Ensure server apps is Running")
	print("  dead                          -- -- Ensure server apps is Stopped")
	print("  start                         -- -- Start server apps")
	print("  stop                          -- -- Stop server apps")
	print("  clean                         -- -- Clean server apps")
	print("  stopcln                       -- -- Stop&Clean server apps")
	print("  rmcore                        -- -- Remove core-dumps of server apps")
	print("GROUP like: AllServices|AllFront|AllProbe|...")
	print("CTR   like: PD|ZJ|BJ")
	print("SRV   like: monprobe|monfront|...")
	print("SRVNO like: 1|3,5,7|10-20|...")

def startDaemon():
	"""
		exec python file task_daemon.py and start daemon
	"""
	try:
		os.system('python %s start'%(cfg.FILE_NAME_DAEMON))
		time.sleep(0.1)
	except Exception as e:
		print(traceback.format_exc())

def genTaskInfo(**option):
	"""
	gen task_info
	args:
		the key of option may be has cmd, ctr, srv ....
	"""
	opt_str = cfg.FLAG_NULL
	for key, value in option.items():
		if key != cfg.CMD:
			opt_str = opt_str + cfg.FLAG_BLANK + cfg.DMINUS + key + cfg.FLAG_BLANK + value
	tid = option[cfg.TID] if option.get(cfg.TID) else 0
	task_info = TaskInfo(state=cfg.FLAG_TASK_START, TID=tid, \
		PID=int(cfg.PID), exec_time=0, cmd=option[cfg.CMD], cmdline=opt_str.strip())
	return task_info

def notifyDaemon(info):
	"""
	start daemon and notify daemon info
	args:
		[HEAD][NTF]int(time.time()) * 100000 + int(cfg.PID)\r\n + [TASK]... for Taskstart
		[HEAD][NTF]int(time.time()) * 100000 + int(cfg.PID)\r\n + [TASK]... + result_info for Taskend 
	
	return:
	
	"""
	try:
		startDaemon()
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((cfg.DAEMON_IP, cfg.DAEMON_PORT))
		sock.send(info + cfg.TIP_INFO_EOF)
		sock.close()
	except Exception as e:
		print('notifyDaemon failed!')
		print(traceback.format_exc())

def notifyTaskStart(taskinfo):
	"""
	set task_info.state = start and notify daemon
	
	args:
		taskinfo: class TaskInfo instance
	"""
	taskinfo.setState(cfg.FLAG_TASK_START)
	notifyDaemon(genNtfHead() + taskinfo.encode())

def notifyTaskEnd(taskinfo, result):
	"""
	set task_info.state = start and notify daemon
	
	args:
		taskinfo: class TaskInfo instance
	"""
	taskinfo.setState(cfg.FLAG_TASK_END)
	info = cfg.FLAG_NULL
	for val in result:
		info = info + cfg.DCOLON.join(val) + cfg.NEWLINE
	result_info = cfg.TIP_RESULT_START + cfg.NEWLINE + info + cfg.TIP_RESULT_END + cfg.NEWLINE
	notifyDaemon(genNtfHead() + taskinfo.encode() + result_info)

def getObject(**option):
	"""
	get objs_map through analysis service.list and start.list
	args:
		option keys include grp, ctr, srv, srvno, ictr, isrv, isrvno, opt, iopt
		
	return:
		objs_map: key is ipaddr and val is a dic which key is srv, val is list( [(ctr, srvno, args)])
	"""
	objs_list = []

	keywords = cfg.FLAG_NULL
	output = cfg.FLAG_NULL
	group = cfg.DEFAULT_GRP

	for key in option:
		if key == cfg.CTR:
			keywords = keywords + cfg.DATACENTER + cfg.EQUAL + option[key].strip() + cfg.SEMICOLON
		if key == cfg.SRV:
			keywords = keywords + cfg.APPNAME + cfg.EQUAL + option[key].strip() + cfg.SEMICOLON
		if key == cfg.SRVNO:
			keywords = keywords + cfg.APPNO + cfg.EQUAL + option[key].strip() + cfg.SEMICOLON
		if key == cfg.GRP:
			group = option[key].strip()
		if key == cfg.OPT:
			output = option[key].strip()
		if key == cfg.ICTR:
			keywords = keywords + cfg.DATACENTER + cfg.EQUAL + cfg.EXCLAMATION + option[key].strip() + cfg.SEMICOLON
		if key == cfg.ISRV:
			keywords = keywords + cfg.APPNAME + cfg.EQUAL + cfg.EXCLAMATION + option[key].strip() + cfg.SEMICOLON
		if key == cfg.ISRVNO:
			keywords = keywords + vAPPNO + cfg.EQUAL + cfg.EXCLAMATION + option[key].strip() + cfg.SEMICOLON
		if key == cfg.IOPT:
			output = cfg.EXCLAMATION + option[key].strip()

	list_start = getcfg(cfg.FILE_START, keywords, output, group)
	list_service = getcfg(cfg.FILE_SERVICE, keywords, output, group=cfg.FLAG_NULL)

	list_start = sorted(set(list_start))
	list_service = sorted(set(list_service))
	if cfg.FLAG_DEBUG:
		print("-----start-----")
		print(list_start)
		print("-----service-----")
		print(list_service)
	for start_line in list_start:
		f_start_list = start_line.strip().split()
		for service_line in list_service:
			f_service_list = service_line.strip().split()
			if f_start_list[0] == f_service_list[0]:
				i = 1
				line_str = cfg.FLAG_NULL
				while i < len(f_start_list):
					line_str = line_str + f_start_list[i] + cfg.FLAG_BLANK
					i += 1
				objs_list.append(f_start_list[0] + cfg.FLAG_BLANK + f_service_list[4] + cfg.FLAG_BLANK + line_str + cfg.NEWLINE)
				break
	return convObjects(objs_list)

def convObjects(objs_list):
	"""
	convert objs_list to objs_map
	
	Args:
		objs_list like [PD.sysagent.1 ....]
	
	returns:
		objs_map like {172.1.128.170:{sysagent:[(PD, sysagent, 1)],..},...}
	"""
	srv_map = {} # {srv : [(ctr, srvno, args)]}
	objs_map = {} # { ip : [srv_map]}
	pre_srv = cfg.FLAG_NULL
	for objs in objs_list:
		token_list = objs.split()
		args = cfg.FLAG_BLANK.join(token_list[5:])
		ip, ctr, srv, srvno = token_list[1:5]
		## ip exist?
		if ip in objs_map:
			if srv in objs_map[ip]:
				objs_map[ip][srv].append((ctr, srvno, args))
			else:
				objs_map[ip][srv] = [(ctr, srvno, args)]
		else:
			srv_map = {}
			srv_map[srv] = [(ctr, srvno, args)]
			objs_map[ip] = srv_map
	return objs_map

def ShowObjsInfo(objs_map):
	"""
	transfer objs_map to info_map which key is srvid and print info_map
	"""
	info_map = {}
	for ip in objs_map.keys():
		srv_map = objs_map[ip]
		for srv in srv_map.keys():
			srv_list = srv_map[srv]
			for ctr, srvno, args in srv_list:
				srvid = "%s.%s.%03d"%(ctr, srv, int(srvno))
				info_map[srvid] = (ip, srv, args)

	iCount = 0
	info_keys = sorted(info_map.keys())
	for key in info_keys:
		iCount += 1
		print("[%s]%03d: %-30s %-20s ./%s %s"%(cfg.CMD_INFO, iCount, key, info_map[key][0], info_map[key][1], info_map[key][2]))

def getLocalHostname():
	return cfg.HOSTNAME

def genTransferZip(srcpath):
	"""
	gen zip file of srcpath for exec put
	"""
	try:
		cwd = os.getcwd()
		os.chdir(cfg.WORK_BASE)
		zip_dir([(srcpath,'')], cfg.FILE_NAME_TRANSZIP)
		os.chdir(cwd)
		if cfg.FLAG_DEBUG:
			print("Zip finished")
	except Exception as e:
		print(traceback.format_exc())
		info = 'make zip file Failed!'
		doExit(0, info)

def delTransferZip():
	"""
	after transmit zip file and delete the zip file
	"""
	zipfile = cfg.WORK_BASE + cfg.SEP + cfg.FILE_NAME_TRANSZIP
	delFilepath(zipfile)

def genConsoleZip():
	"""
	gen zip file of console dictioary for deploy console 
	"""
	try:
		cwd = os.getcwd()
		os.chdir(cfg.WORK_BASE)
		zip_dir(cfg.FILE_LISTS_ALL, cfg.FILE_NAME_PKGZIP)
		os.chdir(cwd)
		if cfg.FLAG_DEBUG:
			print("Zip finished")
	except Exception as e:
		print(traceback.format_exc())
		info = 'make zip file Failed!'
		doExit(0, info)

def delConsoleZip():
	"""
	after send zip file and del console zip file
	"""
	zipfile = cfg.WORK_BASE + cfg.SEP + cfg.FILE_NAME_PKGZIP
	delFilepath(zipfile)

def genRtnMapOnIP(objs_map):
	"""
	init rtn_map for key is ip 
	"""
	try:
		rtn_map = {}
		## {ip : flag}
		for ip in list(objs_map.keys()):
			rtn_map[ip] = False
	except Exception:
		print(traceback.format_exc())
	finally:
		return rtn_map

def getSrvIdFromIp(objs_map, ip):
	srvid_list = []
	srv_list = list(objs_map[ip].keys())
	for srv in srv_list:
		## init srvid rtn
		for srvid_item in objs_map[ip][srv]:
			ctr, srvno, args = srvid_item
			srvid = ctr + cfg.DOT + srv + cfg.DOT + srvno
			srvid_list.append(srvid)
	return srvid_list	

def genRtnMapOnSrvID(objs_map):
	"""
	init rtn_map for key is srvid
	"""
	try:
		rtn_map = {}
		for ip in list(objs_map.keys()):
			srv_list = list(objs_map[ip].keys())
			for srv in srv_list:
				## init srvid rtn
				for srvid_list in objs_map[ip][srv]:
					ctr, srvno, args = srvid_list
					srvid = ctr + cfg.DOT + srv + cfg.DOT + srvno
					rtn_map[srvid] = False
		return rtn_map
	except Exception:
		print(traceback.format_exc())
	finally:
		return rtn_map

def addFilesMap(files_map, ip, file_list):
	"""
	add a element for files_map with key is ip and val is file_list
	"""
	try:
		if ip in files_map:
			files_list = files_map[ip] | file_list
			#files_list = set(files_list)
			files_map[ip] = files_list
		else:
			files_map[ip] = file_list
	except Exception:
		print(traceback.format_exc())
	finally:
		return files_map

def genXmlZips(item):
	"""
	gen zip file for copyXml,the zip file include files in the dictionary of /config/
	Args:
		item:/config/
	Returns:
		files_map:zip files and md5 files
	"""
	try:
		files_map = {}
		copy_map = {}
		file_list = set()
		#获取对象对应的版本目录
		objectPath = getObjectPath(cfg.XML)
		zip_filename = item + cfg.DOT + cfg.ALL + cfg.FILE_SUF_ZIP
		zip_filepath_src = objectPath + cfg.SEP_COMM + zip_filename
		md5_filename = zip_filename + cfg.FILE_SUF_MD5
		md5_filepath_src = zip_filepath_src + cfg.FILE_SUF_MD5
		if not os.path.isfile(md5_filepath_src):
			## gen md5file ?? NO
			print("no md5_filepath_src")
			return files_map
		else:
			if not md5check(zip_filepath_src, md5_filepath_src):
				print("no match")
				## MD5 check error
				return files_map
		zip_filepath_dst = cfg.WORK_DIR + cfg.SEP_COMM + cfg.WORK_TEMP + cfg.SEP_COMM + zip_filename + cfg.DOT + cfg.PID
		md5_filepath_dst = cfg.WORK_DIR + cfg.SEP_COMM + cfg.WORK_TEMP + cfg.SEP_COMM + md5_filename + cfg.DOT + cfg.PID

		copy_map[zip_filepath_dst] = zip_filepath_src
		copy_map[md5_filepath_dst] = md5_filepath_src
		file_list.add(zip_filepath_dst)
		file_list.add(md5_filepath_dst)
		files_map['*'] = file_list

		cwd = os.getcwd()
		os.chdir(cfg.WORK_BASE)
		## copy src to dst
		for dst, src in list(copy_map.items()):
			if cfg.FLAG_DEBUG:
				print('copy [%s] to [%s]'%(src, dst))
			shutil.copyfile(src, dst)
		os.chdir(cwd)
	except Exception as e:
		print(traceback.format_exc())
		info = 'copy files Failed!'
		doExit(0, info)
	else:
		return files_map

def genServerZips(objs_map):
	"""
	gen zip file for deployServer,the zip file include files in the dictionary of /app/release/
	"""
	try:
		objectPath = getObjectPath(cfg.SERVER)
		host_map = loadHostMap()
		files_list = set()
		## init rtn_map to False
		## ip : file_list
		files_map = {}
		## dst : src
		copy_map = {}

		iprelay_map, ipsub_map = loadRelayFile()
		for ip in objs_map:
			if ip not in host_map:
				print('Warn: host[' + ip + '] os type unknown!' )
				continue
			ostype, host = host_map[ip]
			srv_list = list(objs_map[ip].keys())
			file_list = set()
			for srv in srv_list:
				## files
				zip_filename = srv + cfg.DOT + ostype + cfg.FILE_SUF_ZIP
				zip_filepath_src = objectPath + cfg.SEP_COMM + zip_filename
				if not os.path.isfile(zip_filepath_src):
					zip_filename = srv + cfg.DOT + cfg.ALL + cfg.FILE_SUF_ZIP
					zip_filepath_src = objectPath + cfg.SEP_COMM + zip_filename
					if not os.path.isfile(zip_filepath_src):
						### ZIP not found
						continue
				md5_filename = zip_filename + cfg.FILE_SUF_MD5
				md5_filepath_src = zip_filepath_src + cfg.FILE_SUF_MD5
				if not os.path.isfile(md5_filepath_src):
					## gen md5file ?? NO
					continue
				else:
					if not md5check(zip_filepath_src, md5_filepath_src):
						## MD5 check error
						continue
				zip_filepath_dst = cfg.WORK_DIR + cfg.SEP_COMM + cfg.WORK_TEMP + cfg.SEP_COMM + zip_filename + cfg.DOT + cfg.PID
				md5_filepath_dst = cfg.WORK_DIR + cfg.SEP_COMM + cfg.WORK_TEMP + cfg.SEP_COMM + md5_filename + cfg.DOT + cfg.PID

				copy_map[zip_filepath_dst] = zip_filepath_src
				copy_map[md5_filepath_dst] = md5_filepath_src
				file_list.add(zip_filepath_dst)
				file_list.add(md5_filepath_dst)
				files_list.add(zip_filepath_dst)
				files_list.add(md5_filepath_dst)

			files_map = addFilesMap(files_map, ip, file_list)

			if ip in iprelay_map:
				for iprelay in iprelay_map[ip]:
					files_map = addFilesMap(files_map, iprelay, file_list)
		cwd = os.getcwd()
		os.chdir(cfg.WORK_BASE)
		## copy src to dst
		for dst, src in list(copy_map.items()):
			if cfg.FLAG_DEBUG:
				print('copy [%s] to [%s]'%(src, dst))
			shutil.copyfile(src, dst)
		os.chdir(cwd)
	except Exception as e:
		print(traceback.format_exc())
		info = 'copy files Failed!'
		doExit(0, info)
	else:
		return files_map, files_list

def getUndeployObjs(objs_map):
	"""
	修改服务对象映射，执行undeploy应该先undeploy没有后继或者后继都被undeploy的节点
	"""
	ip_list = list(objs_map.keys())
	host_map = loadHostMap()
	chost_list = list(host_map.keys())
	##chost_list存在但ip_list不存在的元素
	reserve_hosts = set(chost_list) - set(ip_list)
	iprelay_map, ipsub_map = loadRelayFile()
	for ip in ip_list:
		if ip in chost_list:
			if ip in ipsub_map:
				ipsub_list = ipsub_map[ip]
				if cfg.FLAG_DEBUG:
					print('ipsub_list for ' + ip + cfg.NEWLINE + cfg.FLAG_BLANK.join(ipsub_list))
				##ipsub_list 与 reserve_hosts的交集
				if len(set(ipsub_list) & set(reserve_hosts)) > 0:
					del objs_map[ip]
					reserve_hosts.add(ip)
		else:
			del objs_map[ip]
	return objs_map

def getXmlObjs(objs_map, item):
	"""
	找到需要部署XML的服务对象
	"""
	##1.for ip in objs_
	print("getXmlObjs")
	if cfg.XML_SRVS.get(item):
		srv_list = cfg.XML_SRVS[item]
		for ip in objs_map.keys():
			flag = False
			for srv in objs_map[ip].keys():
				if srv in srv_list:
					flag = True
				else:
					del objs_map[ip][srv]
			if not flag:
				del objs_map[ip]
	return objs_map

def getNextIpList(ip):
	"""
	获取当前主机所对应的后继ip信息
	"""
	ip_relay_list = []
	f = open(cfg.FILE_RELAY)
	lines_list = f.readlines()
	for line in lines_list:
		line = line.strip()
		if (not line) or line.startswith(cfg.FLAG_TIPS):
			continue
		else:
			ipaddr, iprelay = line.split()
			if iprelay == ip:
				if len(ip_relay_list) == 0:
					ip_relay_list.append(ipaddr)
				else:
					ip_relay_list = [ipaddr]
	return ip_relay_list

def getNextMap(ip_list):
	"""
	获得ip_list中每个ip所对应的后继ip
	"""
	## iprelay_map:  ip -> [relay1, relay2, ...]
	iprelay_map, ipsub_map = loadRelayFile()
	## ipnext_map:   ipnext -> ["relay1,relay2,...,ip", ...]
	ipnext_map = {}
	for ip in ip_list:
		## need relay ?
		if ip in iprelay_map.keys() and len(iprelay_map[ip]) > 0:
			## if RELAY: cached
			iprelay_list = iprelay_map[ip]
			ipnext = iprelay_list.pop(0)
			iprelay_list.append(ip)
			if ipnext in ipnext_map.keys():
				ipnext_map[ipnext].append(cfg.COMMA.join(iprelay_list))
			else:
				ipnext_map[ipnext] = [cfg.COMMA.join(iprelay_list)]
		else:
			if ip in ipnext_map.keys():
				## else: do with no relay
				ipnext_map[ip].append(cfg.FLAG_NULL)
			else:
				ipnext_map[ip] = [cfg.FLAG_NULL]
	return ipnext_map

## [''] ['151', ''] ['', '']['146,151', '146,153', '152, ', '']

def getNextMapForIP(ipnext_map, ip):
	"""
	修改为当前主机所对应的后继ip信息
	"""
	ipnext_map_new = {}
	if ip in ipnext_map:
		iprelay_list = ipnext_map[ip]
		for iprelay in iprelay_list:
			if iprelay == cfg.FLAG_NULL:
				ipnext_map_new[cfg.FLAG_NULL] = [cfg.FLAG_NULL]
				continue

			if iprelay.find(cfg.COMMA)!= -1:
				ipnext,ipnext_tail = iprelay.strip().split(cfg.COMMA)
			#忽略','
			else:
				ipnext = iprelay
				ipnext_tail = ""

			if ipnext in ipnext_map_new:
				ipnext_map_new[ipnext].append(ipnext_tail)
			else:
				ipnext_map_new[ipnext] = [ipnext_tail]
	return ipnext_map_new

def getFileListbyIP(files_map, ip):
	"""
	获取对应ip的文件列表
	Args：
		files_map：为ip和文件列表的映射
	"""
	if ip in files_map:
		return files_map[ip]
	elif '*' in files_map:
		return files_map['*']
	else:
		return []


def getTargetIPList(ipnext_map, ip):
	ipnext_list = ipnext_map[ip]
	ip_list = []
	for token in ipnext_list:
		token_list = token.split(cfg.COMMA)
		ip_addr = cfg.FLAG_NULL
		while (ip_addr == cfg.FLAG_NULL and len(token_list)>0):
			ip_addr = token_list.pop().strip()		
		if ip_addr == cfg.FLAG_NULL:
			ip_list.append(ip)
		else:
			ip_list.append(ip_addr)
	return ip_list
	
def genConnErrInfo(opt_map, ip, info_out):
	
	info = cfg.CMD_CONNERR_TIP
	ip_list = getTargetIPList(opt_map['ipnext_map'], ip)
	
	if opt_map['cmd1'] in cfg.CMDS_HOSTLEVEL:
		for ip_addr in ip_list:
			info_out += cfg.DCOLON.join([opt_map['cmd1'], ip_addr, ip, info]) + cfg.NEWLINE
	else:
		for ip_addr in ip_list:		
			srvid_list = getSrvIdFromIp(opt_map['objs_map'], ip_addr)
			for srvid in srvid_list:
				info_out += cfg.DCOLON.join([opt_map['cmd1'], ip_addr, srvid, info]) + cfg.NEWLINE
	if cfg.FLAG_DEBUG:
		print("SSH err :" + ip)
	return info_out

def emptyCallback(request,result):
	pass
#	print('Task [%d] done'%(request.requestID))

def ShowHostInfo(objs_map):
	"""
	输出host.list 
	"""
	host_map = loadHostMap()
	ip_list = sorted(objs_map.keys())
	iCount = 0
	for ip in ip_list:
		iCount += 1
		host_info = host_map.get(ip, ('(unknown)', '(unknown)'))
		print("[%s]%03d: %-20s %6s %s"%(cfg.CMD_INFO, iCount, ip, host_info[0], host_info[1]))

def ShowRelayInfo(objs_map):
	"""
	输出relay.list
	"""
	iprelay_map, ipsub_map = loadRelayFile()
	ip_list = sorted(objs_map.keys())
	iCount = 0
	for ip in ip_list:
		iCount += 1
		relay_info = iprelay_map.get(ip, ['(localhost)'])
		print("[%s]%03d: %-20s %s"%(cfg.CMD_INFO, iCount, ip, cfg.COMMA.join(relay_info)))

def printCmdResult(cmdname, ip, cmd, result):
	"""
	print the result from exec cmd in a specific forma like "%s::%s::%s::%s"
	"""
	print("%s::%s::%s::%s"%(cmdname, ip, cmd, result))

## Level1
def showInfoCmd(**option):
	"""
	执行指令info时，根据给定的参数输出不同结果
	Args:
		默认情况为‘app’ 执行ShowObjsInfo，输出
	example：
		option['args'] = relay 则执行ShowRelayInfo
		option['args'] = host 
	"""
	objs_map = getObject(**option)
	args = option.get(cfg.ARGS, 'app')
	if args == 'relay':
		ShowRelayInfo(objs_map)
	elif args == 'host':
		ShowHostInfo(objs_map)
	else:
		ShowObjsInfo(objs_map)

def appctrlCmd(cmdname, ip, ctr, srv, srvno, args):
	"""
	执行服务启停清理等操作
	"""
	## get OS_TYPE
	os.chmod(cfg.FILE_APPCTRL,stat.S_IRWXU|stat.S_IRGRP|stat.S_IWGRP|stat.S_IROTH)
	cmd = '%s %s %s %s %s %s %s'%(cfg.FILE_APPCTRL, cmdname, ip, ctr, srv, srvno, args)
	os.system(cmd)
	#print('%s::%s::%s::%s'%(cmdname, ip, ctr + DOT + srv + DOT + srvno, args))

def updateCmd(*args):
	"""
	
	copyXml:(files_list, srv, cfg.XML_CONFIG)
	deployServer:(files_list, srv)
	"""
	try:
		filename_map = {}
		for filepath in args[0]:
			basename = os.path.basename(filepath)
			basename, pid = os.path.splitext(basename)
			filename_map[basename] = filepath

		if len(args) == 3:
			path_name = args[2]
		elif len(args) == 2:
			path_name = args[1]
		if path_name + cfg.DOT + cfg.OS_TYPE + cfg.FILE_SUF_ZIP in filename_map and \
			path_name + cfg.DOT + cfg.OS_TYPE + cfg.FILE_SUF_ZIP + cfg.FILE_SUF_MD5 in filename_map:
			zipfilepath = filename_map[path_name + cfg.DOT + cfg.OS_TYPE + cfg.FILE_SUF_ZIP]
			md5filepath = filename_map[path_name + cfg.DOT + cfg.OS_TYPE + cfg.FILE_SUF_ZIP + cfg.FILE_SUF_MD5]
		elif path_name + cfg.DOT + cfg.ALL + cfg.FILE_SUF_ZIP in filename_map and \
			path_name + cfg.DOT + cfg.ALL + cfg.FILE_SUF_ZIP + cfg.FILE_SUF_MD5 in filename_map:
			zipfilepath = filename_map[path_name + cfg.DOT + cfg.ALL + cfg.FILE_SUF_ZIP]
			md5filepath = filename_map[path_name + cfg.DOT + cfg.ALL  + cfg.FILE_SUF_ZIP + cfg.FILE_SUF_MD5]
		else:
			print("ZIP not found with: "+ args[2])
			return 1
		if len(args) == 3:
			updateSrv(args[1], cfg.WORK_BASE + cfg.SEP + zipfilepath, cfg.WORK_BASE + cfg.SEP + md5filepath, args[2])
		elif len(args) == 2:
			updateSrv(args[1], cfg.WORK_BASE + cfg.SEP + zipfilepath, cfg.WORK_BASE + cfg.SEP + md5filepath)

#		print("UPDATE: " + args[1], cfg.WORK_BASE + cfg.SEP + zipfilepath)
		return 0
	except Exception as e :
		print(traceback.format_exc())
		return 1

def copyXmlCmd(cmdname, ip, ctr, srv, srvno):
	"""
	exec the cmd for copyXml and print the result in a specific forma
	
	args:
		cmdname:designated which cmd need exec for copyXml
		ip:designated exec cmdname in which machine
		ctr, srv, srvno:designated which file is need
	returns:
		0 indicate succ
		1 indicate failed
	"""
	try:
		deploySrv(srv, ctr, srvno, cfg.XML_CONFIG)
		printCmdResult(cmdname, ip, ctr + cfg.DOT + srv + cfg.DOT + srvno, 'SUCC')
		return 0
	except Exception as e:
		print(traceback.format_exc())
		return 1

def deployServerCmd(cmdname, ip, ctr, srv, srvno):
	"""
	exec the cmd for deployServer and print the result in a specific forma
	args:
		cmdname:designated which cmd need exec for deployServer
		ip:designated exec cmdname in or copy files to which machine
		ctr, srv, srvno:designated which file is need
	returns:
		0 indicate succ
		1 indicate failed
	"""
	try:
		deploySrv(srv, ctr,srvno)
		printCmdResult(cmdname, ip, ctr + cfg.DOT + srv + cfg.DOT + srvno, 'SUCC')
		return 0
	except Exception as e:
		print(traceback.format_exc())
		return 1

def undeployServerCmd(cmdname, ip, ctr, srv, srvno):
	"""
	exec the cmd for undeployServer and print the result in a specific forma
	args:
		cmdname:designated which cmd need exec for undeployServer
		ip:designated exec cmdnameor del files in which machine
		ctr, srv, srvno:designated which file is need
	returns:
		0 indicate succ
		1 indicate failed
	"""
	try:
		undeploySrv(srv, srvno)
		printCmdResult(cmdname, ip, ctr + cfg.DOT + srv + cfg.DOT + srvno, 'SUCC')
		return 0
	except Exception as e :
		print(traceback.format_exc())
		return 1

def deployConsoleCmd(cmdname, ip):
	"""
	print the result from exec deploy console in a specific forma
	"""
	## return OS_TYPE info
	printCmdResult(cmdname, ip, cfg.OS_TYPE, cfg.HOSTNAME)

def undeployConsoleCmd(cmdname, ip):
	"""
	print the result from exec undeploy console in a specific forma
	"""
	try:
		printCmdResult(cmdname, ip, cfg.OS_TYPE, cfg.HOSTNAME)
		delFilepath(cfg.DEPLOY_PATH)
		delFilepath(cfg.WORK_PATH)		
		for filename in os.listdir(cfg.WORK_BASE):
			m = re.match("%s|%s"%(cfg.REGEX_CONSOLEZIP,cfg.REGEX_OPTMAP), filename)
			if (m is not None): 
				delFilepath(os.path.join(cfg.WORK_BASE,filename))
		return 0
	except Exception as e :
		print(traceback.format_exc())
		return 1

def RunCmd(cmdname, ip, cmdline):
	"""
	print the result from exec run in a specific forma
	"""
	try:
		## os.system()
		result = os.popen(cmdline,'r').read()
		printCmdResult(cmdname, ip, cmdline, result)
		return 0
	except Exception as e :
		print(traceback.format_exc())
		return 1

def PutCmd(cmdname, ip, file_list, src, dst):
	"""
	print the result from exec put in a specific forma
	"""
	try:
		## os.system()
		for filename in file_list:
			filepath = cfg.WORK_BASE + cfg.SEP_COMM + filename
			if os.path.exists(filepath):
				## unzip to dst
				unzip_file(filepath, dst)
				printCmdResult(cmdname, ip, src, dst)
			else:
				printCmdResult(cmdname, ip, src, 'failed')
		return 0
	except Exception as e :
		print(traceback.format_exc())
		return 1

def Init(**option):
	"""
	用于在执行一级指令之前进行初始化
	"""
	result = []
	objs_map = getObject(**option)
	opt_map = {}
	opt_map['cmd1'] = option[cfg.CMD]
	opt_map['cmd2'] = option[cfg.CMD] + cfg.SUFF_CMD
	opt_map['host'] = cfg.HOSTNAME
	opt_map['objs_map'] = objs_map
	opt_map['cmd_list'] = []
	opt_map['cmd_flag'] = cfg.EXEC_TGT
	opt_map['files_map'] = {}
	return result, objs_map, opt_map

def execLocal(opt_map):
	"""
	本地执行部分
	"""
	objs_map = opt_map['objs_map']
	ip = opt_map['ip'].strip()
	cmd1 = opt_map['cmd1']
	cmd2 = opt_map['cmd2']
	if cfg.FLAG_DEBUG:
		print("execLocal at: " + ip + ';' + cfg.PID)
		## localhost is no Consolehost
		print("opt_map in EXECLOCAL at " + ip)
		print(opt_map)
	if 'files_map' in opt_map:
		files_map = opt_map['files_map']
		files_list = getFileListbyIP(files_map, ip)
	else:
		files_list = []
	try:
		if opt_map['cmd_flag'] == cfg.EXEC_ALL or cfg.FLAG_NULL in opt_map['ipnext_map']:
			if ip in objs_map:
				if cmd2 == 'deployConsoleCmd' :
					deployConsoleCmd(cmd1, ip)
				elif cmd2 == 'undeployConsoleCmd' and cfg.HOSTNAME != opt_map['host']:
					undeployConsoleCmd(cmd1, ip)
				elif cmd1 == cfg.CMD_RUN or (cmd1 == cfg.CMD_RUN_R and cfg.HOSTNAME != opt_map['host']):
					RunCmd(cmd1, ip, cmd2)
				elif cmd1 == cfg.CMD_PUT:
					PutCmd(cmd1, ip, files_list, opt_map[cfg.SRC], opt_map[cfg.DST])
				else:
					dic_srvs = objs_map[ip]
					for srv in list(dic_srvs.keys()):
						if cmd2 == 'deployServerCmd':
							if len(files_list) > 0:
								if 1 == updateCmd(files_list, srv):
									continue
							else:
								continue
						elif cmd2 == 'copyXmlCmd':
							if len(files_list) > 0:
								if 1 == updateCmd(files_list, srv, cfg.XML_CONFIG):
									continue
							else:
								continue

						srvobjs = dic_srvs[srv]
						for srvobj in srvobjs:
							ctr = srvobj[0]
							srvno = srvobj[1]
							args = srvobj[2]
							if cfg.FLAG_DEBUG:
								print("ip[%s] [%s] [%s] %s.%s.%s [%s]"%(ip, cmd1, cmd2, srvobj[0], srv, srvobj[1], srvobj[2]))
							### exec cmd2
							if cmd2 == 'deployServerCmd' :
								deployServerCmd(cmd1, ip, ctr, srv, srvno)
							elif cmd2 == 'undeployServerCmd' :
								undeployServerCmd(cmd1, ip, ctr, srv, srvno)
							elif cmd2 == 'copyXmlCmd' :
								copyXmlCmd(cmd1, ip, ctr, srv, srvno)
							elif cmd1 in cfg.CMDS_APP:
								appctrlCmd(cmd1, ip, ctr, srv, srvno, args)
							else:
								pass

		if cfg.HOSTNAME != opt_map['host']:
			if cmd1 == cfg.CMD_COPYXML:
				return 0
	except Exception:
		print(traceback.format_exc())
		return 1
	finally:
		if cfg.HOSTNAME != opt_map['host']:
			for filename in files_list:
				filepath = cfg.WORK_BASE + cfg.SEP_COMM + filename
				if cfg.FLAG_DEBUG:
					print("Del "+ filepath)
				delFilepath(filepath)

def execRemote(TID, PID, ip, opt_map, rtn_queue):
	"""
	远程执行部分
	"""
	global g_Lock
	#global g_iFinish
	result = cfg.CMD_FAIL
	info_out = cfg.FLAG_NULL
	info_err = cfg.FLAG_NULL
	#ipnext_map = opt_map['ipnext_map']
	#task_count = len(ipnext_map[ip])
	opt_map_remote = copy.deepcopy(opt_map)
	try:
		filename_opt = 'opt_map.'+ PID + cfg.DOT + TID
		filepath_opt = cfg.WORK_BASE + cfg.SEP_COMM + filename_opt

		if 'files_map' in opt_map:
			files_map = opt_map['files_map']
		else:
			files_map = {}

		cmd_list = opt_map['cmd_list'][:]
		cmd_flag = opt_map['cmd_flag']
		### !!!!  Windows maybe error
		cmd = 'cd;. .bash_profile; cd %s && python %s --cmd execCmd --file \'../../%s\''%(cfg.WORK_DIR + cfg.SEP_COMM + cfg.WORK_SCR, cfg.FILE_NAME_MAIN, filename_opt)
		cmd_list.append(cmd)
		if cfg.FLAG_DEBUG:
			g_Lock.acquire()
			print("SSH to " + ip + " start")
			g_Lock.release()

		if FLAG_SSH == cfg.FLAG_SSH_PARA:
			result, ssh = ssh_conn(ip, cfg.SSH_PORT, cfg.USER, cfg.SSH_CASE_PSWD, cfg.USER_PSWD)
			if result != cfg.CMD_SUCC:
				return 1
			result, info_out, info_err = ssh_exec(ssh, ['hostname'], case=cfg.SSH_CASE_IGN)
			if result != cfg.CMD_SUCC or len(info_out.strip()) == 0:
				return 1
		else:
			result, info_out, info_err = ssh_exec(ip, ['hostname'], case=cfg.SSH_CASE_IGN)
			if result != cfg.CMD_SUCC or len(info_out.strip()) == 0:
				return 1

		if cfg.FLAG_DEBUG:
			g_Lock.acquire()
			print('IP:['+ip+']  FLAG_SSH = ' + str(FLAG_SSH))
			g_Lock.release()
		hostname = info_out.strip()
		if result == cfg.CMD_SUCC and hostname != cfg.FLAG_NULL:
			if hostname != cfg.HOSTNAME and hostname != opt_map['host']:  ## not localhost
				if ip in files_map:
					file_objs = files_map[ip]
				elif '*' in files_map:
					file_objs = files_map['*']
				else:
					file_objs = []

				for file_obj in file_objs:
					if FLAG_SSH == cfg.FLAG_SSH_PARA:
						sftp = ssh_opensftp(ssh)
						result = sftp_put(sftp, file_obj, cfg.WORK_BASE + cfg.SEP_COMM + file_obj)
					else:
						result = sftp_put(ip, file_obj, cfg.WORK_BASE + cfg.SEP_COMM + file_obj)
					if cfg.FLAG_DEBUG:
						g_Lock.acquire()
						print("SFTP:[%s][%s][%d]"%(ip, file_obj, result))
						g_Lock.release()
					if result != cfg.CMD_SUCC:
						return 1
			else:
				## localhost
				if cfg.FLAG_DEBUG:
					g_Lock.acquire()
					print("IP [%s] is localhost"%(ip))
					print("Try to combine ipnext_map with keys ['%s'] and ['']"%(ip))
					print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
					print(opt_map)
					print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
					g_Lock.release()

			ipnext_map_new = getNextMapForIP(opt_map['ipnext_map'], ip)

			## gen pickle file
			opt_map['ipnext_map'] = ipnext_map_new
			opt_map['ip'] = ip
			if cfg.FLAG_DEBUG:
				g_Lock.acquire()
				print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
				print("Update opts with:")
				print(opt_map)
				print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
				g_Lock.release()

			dumpPickle(opt_map, filepath_opt)
			if hostname != cfg.HOSTNAME and hostname != opt_map['host']:  ## not localhost
				if cfg.FLAG_DEBUG:
					g_Lock.acquire()
					print("@@@@@@@ " + cfg.HOSTNAME + " Send file "+ filename_opt + ' to ' + ip)
					g_Lock.release()
				if FLAG_SSH == cfg.FLAG_SSH_PARA:
					sftp = ssh_opensftp(ssh)
					result = sftp_put(sftp, filename_opt, filepath_opt)
				else:
					result = sftp_put(ip, filename_opt, filepath_opt)
				if result != cfg.CMD_SUCC:
					return 1

			if FLAG_SSH == cfg.FLAG_SSH_PARA:
				result, info_out, info_err = ssh_exec(ssh, cmd_list, case=cfg.SSH_CASE_NIGN)
				ssh_close(ssh)
			else:
				result, info_out, info_err = ssh_exec(ip, cmd_list, case=cfg.SSH_CASE_NIGN)
		if cfg.FLAG_DEBUG:
			g_Lock.acquire()
			print("SSH to " + ip + " end")
			g_Lock.release()
		return 0
	except Exception as e:
		print(traceback.format_exc())
		return 1
	finally:
		### delete local genarated pickle file
		#g_Lock.acquire()
		#g_iFinish += task_count
		#g_Lock.release()
		if result != cfg.CMD_SUCC:
			info_out = genConnErrInfo(opt_map_remote, ip, info_out)
		info_out_list = info_out.replace('\r', '\n').split('\n')
		for i in range(len(info_out_list)):
			info_out_list[i] = info_out_list[i].strip()
		lines = sorted(set(info_out_list))
		for line in lines:
			line = line.strip()
			if line.startswith(opt_map_remote['cmd1'] + cfg.DCOLON):
				g_Lock.acquire()
				print(line)
				g_Lock.release()

		rtn_queue.put((info_out, info_err))
		delFilepath(filepath_opt)

###!!! relay.list 判断本地IP；避免回环

## Bottom
def execBase(opt_map):
#	global g_iTotal
	opt_map_local = copy.deepcopy(opt_map)
	#print('---opt_map orig ' + PID)
	#print(opt_map)
	ipnext_map = opt_map['ipnext_map']
	out = cfg.FLAG_NULL
	err = cfg.FLAG_NULL
	try:
		## Have remote tasks?
		if (len(list(ipnext_map.keys())) > 1) or ((len(list(ipnext_map.keys())) == 1) and (cfg.FLAG_NULL not in list(ipnext_map.keys()))):
			## enable SSH (paramiko)
			count = 0
			rtn_queue = Queue.Queue()

			#for key in ipnext_map.keys():
			#	g_iTotal += len(ipnext_map[key])

			if cfg.FLAG_TREADPOOL:
				tp = ThreadPool(cfg.SSH_THREADS)
			else:
				threads = []

			for ipnext in list(ipnext_map.keys()):
				if ipnext == cfg.FLAG_NULL:
					continue
				count += 1
				opt_map_remote = copy.deepcopy(opt_map)

				if cfg.FLAG_TREADPOOL:
					## ipnext : nextjump
					## opt_map_remote : full nextjumps, KEYS include ipnext
					req = WorkRequest(execRemote, args=[str(count), cfg.PID, ipnext, opt_map_remote, rtn_queue], kwds={}, callback=emptyCallback)
					tp.putRequest(req)
					if cfg.FLAG_DEBUG:
						print("work request #%s added." % req.requestID)
				else:
					t = threading.Thread(target=execRemote, args=(str(count), cfg.PID, ipnext, opt_map_remote, rtn_queue))
					threads.append(t)

			if not cfg.FLAG_TREADPOOL:
				for i in range(count):
					threads[i].start()
					#threads[i].join()
			while rtn_queue.qsize() != count:
				time.sleep(0.1)
				file(cfg.FILE_PROCESSING, "w+").write("\rProcessing:%.2f%%\r"%((100.0*rtn_queue.qsize())/count))

			if cfg.FLAG_TREADPOOL:
				#tp.wait()
				tp.stop()

			while not rtn_queue.empty():
				rtn = rtn_queue.get()
				out += rtn[0]
				err += rtn[1]

		### 本地执行部分
		if 'ip' in opt_map_local.keys():
			## target node
			execLocal(opt_map_local)
	except Exception as e:
		print(traceback.format_exc())
		return 1, out, err
	else:
		return 0, out, err

## Leve2
def execCmd(**option):
	"""
	通过远程调用ecall主脚本执行的指令部分
	"""
	#option --file filename
	try:
		filename = option['file']
		## file exists?
		if os.path.exists(filename):
			##load file
			opt_map = loadPickle(filename)
			## maybe execlocal, have no return!
			rtn, out, err = execBase(opt_map)
			print('--------RTN [%s]--------'%(cfg.HOSTNAME))
			print(rtn)
			print('--------OUT [%s]--------'%(cfg.HOSTNAME))
			print(out)
			print('--------ERR [%s]--------'%(cfg.HOSTNAME))
			print(err)
			delFilepath(filename)
		else:
			print("Error: opt_map file [" + filename + "] not exists!")
	except Exception :
		print(traceback.format_exc())

def execTopCmd(**option):
	"""
	执行一级指令，通过输入脚本命令直接执行调用
	"""
	try:
		result, objs_map, opt_map = Init(**option)

		if option[cfg.CMD] == cfg.CMD_DEPLOYCONSOLE:
			genConsoleZip()
			cmd_list = []
			cmd = 'unzip -o %s >/dev/null 2>&1 '%(cfg.FILE_NAME_PKGZIP)
			cmd_list.append(cmd)
			cmd = 'cd %s && chmod u+x %s && ./%s'%(cfg.WORK_DIR + cfg.SEP_COMM + cfg.WORK_SHELL, cfg.FILE_NAME_INSTALL, cfg.FILE_NAME_INSTALL)
			cmd_list.append(cmd)
			opt_map['cmd_list'] = cmd_list
			opt_map['cmd_flag'] = cfg.EXEC_ALL
			opt_map['files_map'] = {'*':[cfg.FILE_NAME_PKGZIP]}
		elif option[cfg.CMD] == cfg.CMD_UNDEPLOYCONSOLE:
			## change objs_map
			objs_map = getUndeployObjs(objs_map)
			opt_map['objs_map'] = objs_map
		elif option[cfg.CMD] == cfg.CMD_DEPLOYSERVER:
			files_map, files_list = genServerZips(objs_map)
			opt_map['files_map'] = files_map
		elif option[cfg.CMD] == cfg.CMD_COPYXML:
			## change objs_map
			##目前指定XML目录下的config组
			objs_map = getXmlObjs(objs_map, cfg.XML_CONFIG)
			opt_map['objs_map'] = objs_map
			opt_map['files_map'] = genXmlZips(cfg.XML_CONFIG)
		elif option[cfg.CMD] in (cfg.CMD_RUN, cfg.CMD_RUN_R):
			## change objs_map
			objs_map = getUndeployObjs(objs_map)
			opt_map['objs_map'] = objs_map
			##??opt_map['cmd2'] 是什么？？？ 需要执行的指令串
			opt_map['cmd2'] = option[cfg.ARGS]
		elif option[cfg.CMD] == 'put':
			## change objs_map
			objs_map = getUndeployObjs(objs_map)
			opt_map['objs_map'] = objs_map
			if (not option.get(cfg.SRC)) or (not option.get(cfg.DST)):
				info = 'you should give --src ... --dst ...'
				doExit(1, info)
			opt_map[cfg.SRC] = option[cfg.SRC]
			opt_map[cfg.DST] = option[cfg.DST]
			genTransferZip(option[cfg.SRC])
			opt_map['files_map'] = {'*':[cfg.FILE_NAME_TRANSZIP]}

		opt_map['ipnext_map'] = getNextMap(list(objs_map.keys()))

		rtn, out, err = execBase(opt_map)

		if cfg.FLAG_DEBUG:
			print('++++++++++++++++++OUT++++++++++++++++++')
			print(out)
			print('++++++++++++++++++OUT++++++++++++++++++')
		
		lines = out.replace('\r', '\n').split('\n')
		if option[cfg.CMD] in (cfg.CMD_DEPLOYCONSOLE, cfg.CMD_UNDEPLOYCONSOLE):
			## get OS_TYPE info list
			host_map = loadHostMap()
			for line in lines:
				line = line.strip()
				#print(line)
				if line.startswith(option[cfg.CMD] + cfg.DCOLON):
					tip, ip, ostype, host = line.split(cfg.DCOLON)
					result.append((tip, ip, ostype, host))
					if cfg.FLAG_DEBUG:
						print("get", tip, ip, ostype, host)
					if option[cfg.CMD] == cfg.CMD_DEPLOYCONSOLE and host != cfg.CMD_CONNERR_TIP:
						host_map[ip] = (ostype, host)
					else:
						if ip in host_map:
							del host_map[ip]
			delConsoleZip()
			dumpHostMap(host_map)
		elif option[cfg.CMD] in (cfg.CMD_RUN, cfg.CMD_RUN_R, cfg.CMD_PUT, cfg.CMD_GET):
			for line in lines:
				line = line.strip()
				#print(line)
				if line.startswith(option[cfg.CMD] + cfg.DCOLON):
					tip, ip, cmdline, cmdout = line.split(cfg.DCOLON)
					result.append((tip, ip, cmdline, cmdout))
					if cfg.FLAG_DEBUG:
						print("get", tip, ip, cmdline, cmdout)
			delTransferZip()
		else:
			for line in lines:
				line = line.strip()
				if line.startswith(option[cfg.CMD] + cfg.DCOLON):
					tip, ip, srvid, msg = line.split(cfg.DCOLON)
					result.append((tip, ip, srvid, msg))
					if cfg.FLAG_DEBUG:
						print("get", tip, ip, srvid)

			if option[cfg.CMD] == cfg.CMD_DEPLOYSERVER:
				for filename in files_list:
					filepath = cfg.WORK_BASE + cfg.SEP_COMM + filename
					if cfg.FLAG_DEBUG:
						print("Del "+ filepath)
					delFilepath(filepath)
		return result
	except Exception :
		print(traceback.format_exc())
		return result

def execTopCmd_bak(**option):
	"""
	执行一级指令，通过输入脚本命令直接执行调用
	"""
	try:
		result, objs_map, opt_map = Init(**option)

		if option[cfg.CMD] == cfg.CMD_DEPLOYCONSOLE:
			genConsoleZip()
			cmd_list = []
			cmd = 'unzip -o %s >/dev/null 2>&1 '%(cfg.FILE_NAME_PKGZIP)
			cmd_list.append(cmd)
			cmd = 'cd %s && chmod u+x %s && ./%s'%(cfg.WORK_DIR + cfg.SEP_COMM + cfg.WORK_SHELL, cfg.FILE_NAME_INSTALL, cfg.FILE_NAME_INSTALL)
			cmd_list.append(cmd)
			opt_map['cmd_list'] = cmd_list
			opt_map['cmd_flag'] = cfg.EXEC_ALL
			opt_map['files_map'] = {'*':[cfg.FILE_NAME_PKGZIP]}
		elif option[cfg.CMD] == cfg.CMD_DEPLOYSERVER:
			files_map, files_list = genServerZips(objs_map)
			opt_map['files_map'] = files_map
		elif option[cfg.CMD] == cfg.CMD_UNDEPLOYCONSOLE:
			## change objs_map
			objs_map = getUndeployObjs(objs_map)
			opt_map['objs_map'] = objs_map
		elif option[cfg.CMD] == cfg.CMD_COPYXML:
			## change objs_map
			##目前指定XML目录下的config组
			objs_map = getXmlObjs(objs_map, cfg.XML_CONFIG)
			opt_map['objs_map'] = objs_map
			opt_map['files_map'] = genXmlZips(cfg.XML_CONFIG)
		elif option[cfg.CMD] in (cfg.CMD_RUN, cfg.CMD_RUN_R):
			## change objs_map
			objs_map = getUndeployObjs(objs_map)
			opt_map['objs_map'] = objs_map
			##??opt_map['cmd2'] 是什么？？？
			opt_map['cmd2'] = option[cfg.ARGS]
		elif option[cfg.CMD] == 'put':
			## change objs_map
			objs_map = getUndeployObjs(objs_map)
			opt_map['objs_map'] = objs_map
			if (not option.get(cfg.SRC)) or (not option.get(cfg.DST)):
				info = 'you should give --src ... --dst ...'
				doExit(1, info)
			opt_map[cfg.SRC] = option[cfg.SRC]
			opt_map[cfg.DST] = option[cfg.DST]
			genTransferZip(option[cfg.SRC])
			opt_map['files_map'] = {'*':[cfg.FILE_NAME_TRANSZIP]}

		opt_map['ipnext_map'] = getNextMap(list(objs_map.keys()))
		if option[cfg.CMD] in cfg.CMDS_HOSTLEVEL:
			## {ip : flag}
			rtn_map = genRtnMapOnIP(objs_map)
		else:
			## {srvid : flag}
			rtn_map = genRtnMapOnSrvID(objs_map)

		rtn, out, err = execBase(opt_map)

		print('++++++++++++++++++OUT++++++++++++++++++')
		print(out)
		print('++++++++++++++++++OUT++++++++++++++++++')
		lines = out.replace('\r', '\n').split('\n')
		count = 0

		if option[cfg.CMD] in (cfg.CMD_DEPLOYCONSOLE, cfg.CMD_UNDEPLOYCONSOLE):
			## get OS_TYPE info list
			host_map = loadHostMap()
			for line in lines:
				line = line.strip()
				#print(line)
				if line.startswith(option[cfg.CMD] + cfg.DCOLON):
					tip, ip, ostype, host = line.split(cfg.DCOLON)
					result.append((tip, ip, ostype, host))
					if cfg.FLAG_DEBUG:
						print("get", tip, ip, ostype, host)
					rtn_map[ip] = True
					if option[cfg.CMD] == cfg.CMD_DEPLOYCONSOLE and host != cfg.CMD_CONNERR_TIP:
						host_map[ip] = (ostype, host)
					else:
						if ip in host_map:
							del host_map[ip]
			delConsoleZip()
			dumpHostMap(host_map)
		elif option[cfg.CMD] in (cfg.CMD_RUN, cfg.CMD_RUN_R, cfg.CMD_PUT, cfg.CMD_GET):
			for line in lines:
				line = line.strip()
				#print(line)
				if line.startswith(option[cfg.CMD] + cfg.DCOLON):
					tip, ip, cmdline, cmdout = line.split(cfg.DCOLON)
					result.append((tip, ip, cmdline, cmdout))
					if cfg.FLAG_DEBUG:
						print("get", tip, ip, cmdline, cmdout)
					rtn_map[ip] = True
			delTransferZip()
		else:
			for line in lines:
				line = line.strip()
				if line.startswith(option[cfg.CMD] + cfg.DCOLON):
					tip, ip, srvid, msg = line.split(cfg.DCOLON)
					result.append((tip, ip, srvid, msg))
					if cfg.FLAG_DEBUG:
						print("get", tip, ip, srvid)
					rtn_map[srvid] = True

			if option[cfg.CMD] == cfg.CMD_DEPLOYSERVER:
				for filename in files_list:
					filepath = cfg.WORK_BASE + cfg.SEP_COMM + filename
					if cfg.FLAG_DEBUG:
						print("Del "+ filepath)
					delFilepath(filepath)

		for key in sorted(rtn_map.keys()):
			count += 1
			print("[%03d] %s for [ %-22s] %s"%(count, option[cfg.CMD], key, 'SUCC' if rtn_map[key] else 'FAILED'))
		return result
	except Exception :
		print(traceback.format_exc())
		return result

def Ecall(**option):
	"""
	应用服务管理
	Args:
		option:用于解析列表以及指定执行指令
		example：Ecall(cmd='deployConsole',ctr='PD', srv='monagent')
	"""
	try:
		logEvent('Ecall_Start', '5', 'cmd=\"%s\"'%(option[cfg.CMD]))
		if option[cfg.CMD] in cfg.CMDS_TOP:
			if cfg.FLAG_DEBUG:
				print("option[CMD]=%s"%(option[cfg.CMD]))

			taskinfo = genTaskInfo(**option)
			notifyTaskStart(taskinfo)
			result = execTopCmd(**option)
			notifyTaskEnd(taskinfo, result)
		elif option[cfg.CMD] == cfg.CMD_EXECCMD:
			execCmd(**option)
		elif option[cfg.CMD] == cfg.CMD_INFO:
			showInfoCmd(**option)
		elif option[cfg.CMD] == cfg.CMD_ZIP:
			genConsoleZip()
			if cfg.FLAG_DEBUG:
				print("Gen console zip [" + cfg.WORK_BASE + cfg.SEP_COMM + cfg.FILE_NAME_PKGZIP + ']')
		else:
			Usage()
		logEvent('Ecall_End', '5', 'cmd=\"%s\"'%(option[cfg.CMD]))
	except Exception :
		Usage()

if __name__ == '__main__':
	Dic_Run = {}
	opts, args = getopt.getopt(sys.argv[1:], cfg.OPTION_OPTS, cfg.OPTION_ARGS)
	for op, value in opts:
		op = op.replace(cfg.DMINUS, cfg.FLAG_NULL)
		Dic_Run[op] = value
	Ecall(**Dic_Run)
