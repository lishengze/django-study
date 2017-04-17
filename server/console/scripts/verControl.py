#!/usr/bin/python
# -*- coding: utf-8	-*-
"""
:copyright: (c) 2016 by chen.xh.
:license:BSD.
"""
import os
import sys
import re
from threading import Lock
import time
import traceback
import string
import getopt
import tarfile
import shutil

import config as cfg
from tools import md5sum, doExit, zip_dir, loadVersionMap, dumpVersionMap, sortVersion

lock = Lock()

def Usage():
	print('verControl Usage:')
	print("  python verControl.py --cmd CMD_OPTION  [--args ARGS]")
	print("CMD_OPTION as:")
	print("	 publish      -- 发布新版本 或 覆盖之前版本")
	print("	 rollback     -- 版本回退 ")
	print("	 show         -- 查看版本信息 ")
	print("	 drop|delete  -- 删除版本信息 ")
	print("ARGS as:  OBJ{,OBJ}*:VERSION{;OBJ{,OBJ}*:VERSION}*")
	print("	 'client,xml:VERSION;server:VERSION'")
	print("	 'all:VERSION'")
	print("for rollback:")
	print("  'client,xml:ver=VERSION;server:dt=20121011_10'")
	print("  'all:seq=2'  -- rollback 2 step version")
	print("OBJ can be: [server | client | xml]")
	print("VERSION like: 1.1.0  1.0.0.1 ...")
	
def getCurVersion(object):
	"""
	获取对象的当前版本
	Args:
		object:对象名
	"""
	cur_ver = '0.0.0'
	dir_map = loadVersionMap()
	if dir_map.get(object):
		token = dir_map[object]
		if len(token) > 1:
			cur_ver = token[1][cfg.VL_VERSION_COL]
	return cur_ver
	
def isExistVersion(dir_map, object, version):
	"""
	判断一个给定的对象以及相应的版本信息元素是否在version.list中
	Args:
		dir_map:需要查找对象的字典，从解析version.list得来
		object：指定需要查找元素的key，即查找对象
		version：指定需要查找元素的val，即查找对象的版本信息
	Returns:
		True 表示给定对象以及相应的版本信息存在于version.list中
		False 表示给定对象以及相应的版本信息不存在
	"""
	if dir_map.get(object):
		val_list = dir_map[object]
		for val in val_list:
			if val[cfg.VL_VERSION_COL] == version:
				return True
	return False

def calcVersion(base, delta):
	"""
	根据版本信息增量，重新计算版本信息，默认+1，
	Args:
		base:当前版本信息
		delta:版本信息增量，增量格式：+0.0... -0.0...
	Returns:
		版本号
	"""
	flag = delta[0]
	list_base = base.split(cfg.DOT)
	list_delta = delta[1:].split(cfg.DOT)
	list_version = []
	len_base = len(list_base)
	len_delta = len(list_delta)
	len_version = max(len_base, len_delta)
	for i in range(len_version):
		value = 0
		if i < len_base:
			value = int(list_base[len_base-i-1])
		if i < len_delta:
			if flag == cfg.PLUS:
				value = value + int(list_delta[len_delta-i-1])
			else:
				value = value - int(list_delta[len_delta-i-1])
		if value <= 0:
			list_version.append('0')
		else:
			list_version.append(str(value))
	i = len_version - 1
	while list_version[i] == '0' and i >0:
		i -= 1
	calc_ver = list_version[:i+1]
	return cfg.DOT.join(list(reversed(calc_ver)))	
	
def dispatchObject(object, version):
	"""
	版本发布
	Args:
		object:指定发布对象
		version:指定发布版本信息
	Returns:
		True：表示有需要发布的信息
		False：表示没有需要发布的信息
	"""
	try:
		## like: .../Release/server/1.0.0.0
		dest_path = cfg.DEPLOY_PATH_RELEASE + cfg.SEP + object + cfg.SEP + version
		back_flag = False
		## backup
		if os.path.isdir(dest_path):
			back_path = dest_path + '_bak.' + cfg.PID
			shutil.move(dest_path, back_path)
			back_flag = True
		os.mkdir(dest_path)
		count = 0
		## like: .../Latest/server
		object_path = cfg.DEPLOY_PATH_LATEST + cfg.SEP + object
		if os.path.isdir(object_path):
			os_list = os.listdir(object_path)
			for os_name in os_list:
				## like: .../Latest/server/linux64
				os_path = object_path + cfg.SEP + os_name
				if os.path.isdir(os_path):
					srv_list = os.listdir(os_path)
					for srv_name in srv_list:
						## like: .../Latest/server/linux64/sysagent
						srv_path = os_path + cfg.SEP + srv_name
						zip_filename = srv_name + '.'+ os_name + cfg.FILE_SUF_ZIP
						zip_filepathSrc = os_path + cfg.SEP + zip_filename
						zip_dir([(srv_path, cfg.FLAG_NULL)], zip_filepathSrc)
						zip_filepathDst = dest_path + cfg.SEP + zip_filename
						if os.path.isfile(zip_filepathDst):
							os.remove(zip_filepathDst)
						shutil.move(zip_filepathSrc, zip_filepathDst)
						count += 1
						md5_filepath = zip_filepathDst + cfg.FILE_SUF_MD5
						if os.path.isfile(md5_filepath):
							os.remove(md5_filepath)
						with open(md5_filepath, 'w') as f:
							f.write(md5sum(zip_filepathDst))
	except Exception as e:
		## restore
		if back_flag:
			if os.path.isdir(dest_path):
				shutil.rmtree(dest_path)
			shutil.move(back_path, dest_path)
		print(traceback.format_exc())
		info = "Dispatch Error"
		doExit(1, info)
	else:
		if count > 0:
			## drop backup
			if back_flag:
				shutil.rmtree(back_path)
			return True
		else:
			## restore ?? not yet
			print("Dispatch nothing !!")
			return False

def dropObject(object, version):
	"""
	删除发布的版本
	Args:
		object:指定要删除的对象
		version:指定要删除的对象的版本信息
	"""
	try:
		object_path = cfg.DEPLOY_PATH_RELEASE + cfg.SEP + object + cfg.SEP + version
		if os.path.isdir(object_path):
			shutil.rmtree(object_path)
	except Exception as e:
		print((traceback.format_exc()))
		info = "Drop Error"
		doExit(1, info)

def addVersion(dir_map, object, version, flag):
	"""
	添加版本信息到version.list
	Args：
		dir_map：解析version.list得到的对象与版本信息的对应关系
		object：指定需要添加版本信息的对象
		version：指定需要添加的版本信息
		flag:值为True or False
			True 表示该对象需要的版本信息不存在，需要新增一行版本信息
			False 表示该对象需要的版本信息已存在，仅需要修改该对象所对应的版本信息
	"""
	## STATUS 'CFLAG_BLANKH' and COPY files
	Time = time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time()))
	if not flag:
		val_list = dir_map[object]
		if cfg.FLAG_DEBUG:
			print('before add')
			print(val_list)
		for i in range(1, len(val_list)):
			if val_list[i][cfg.VL_STATUS_COL] != cfg.VL_STATUS_DEL:
				val_list[i][cfg.VL_STATUS_COL] = cfg.VL_STATUS_HIS
		newline = list(range(0, cfg.VL_COL_NUM))
		newline[cfg.VL_STATUS_COL] = cfg.VL_STATUS_CUR
		newline[cfg.VL_DATETIME_COL] = Time
		newline[cfg.VL_VERSION_COL] = version
		val_list.append(newline)
		dir_map[object] = val_list
		if cfg.FLAG_DEBUG:
			print('after add')
			print(val_list)
	else:
		#################修改可改变对象时一定要注意
		dir_map[object] = []
		newline_top = list(range(0, cfg.VL_COL_NUM))
		newline_top[cfg.VL_STATUS_COL] = cfg.VL_STATUS
		newline_top[cfg.VL_DATETIME_COL] = cfg.VL_DATETIME
		newline_top[cfg.VL_VERSION_COL] = cfg.VL_VERSION
		dir_map[object] = [newline_top]
		newline = list(range(0, cfg.VL_COL_NUM))
		newline[cfg.VL_STATUS_COL] = cfg.VL_STATUS_CUR
		newline[cfg.VL_DATETIME_COL] = Time
		newline[cfg.VL_VERSION_COL] = version
		dir_map[object].append(newline)
	sortVersion(dir_map)
	showObjectVersion(dir_map, object, version)

def modVersion(dir_map, object, version):
	"""
	修改从解析version.list得到的对象与版本信息的对应关系dir_map
	Args:
		dir_map:解析version.list得到的对象与版本信息的对应关系
		object：指定需要修改版本信息的对象
		version：指定需要修改的版本信息
	"""
	## STATUS 'CH' and COVER files
	if version == cfg.FLAG_NULL:
		return
	Time = time.strftime('%Y%m%d_%H%M%S',time.localtime(time.time()))
	val_list = dir_map[object]
	for i in range(1, len(val_list)):
		if val_list[i][cfg.VL_VERSION_COL] == version:
			if val_list[i][cfg.VL_STATUS_COL] == cfg.VL_STATUS_CUR:
				print("["+ object +"][" + version +"] is CURRENT version.")
				return
			val_list[i][cfg.VL_DATETIME_COL] = Time
			val_list[i][cfg.VL_STATUS_COL] = cfg.VL_STATUS_CUR
		elif version and val_list[i][cfg.VL_STATUS_COL] == cfg.VL_STATUS_CUR:
			val_list[i][cfg.VL_STATUS_COL] = cfg.VL_STATUS_HIS
	dir_map[object] = val_list
	sortVersion(dir_map)
	showObjectVersion(dir_map, object, version)

def dropObjectVersion(dir_map, object, version):
	"""
	删除从解析version.list得到的对象与版本信息的对应关系dir_map中某一行
	Args:
		dir_map:需要删除对象的容器
		object：指定需要删除版本信息的对象
		version：指定需要删除的版本信息
	"""
	## STATUS 'D'  and  RM files
	val_list = dir_map[object]
	for i in range(1, len(val_list)):
		if val_list[i][cfg.VL_VERSION_COL] == version:
			if val_list[i][cfg.VL_STATUS_COL] != cfg.VL_STATUS_CUR:
				val_list[i][cfg.VL_STATUS_COL] = cfg.VL_STATUS_DEL
			else:
				info ='Object[' + object + '] Version[' + version + '] is CURRENT version,cann\'t be droped!'
				print(info)
				return False
	dir_map[object] = val_list
	sortVersion(dir_map)
	showObjectVersion(dir_map, object, version)
	return True

def pubVersion(object, version):
	"""
	发布版本，从/latest/目录下发布指定版本到/release/
	并修改version.list 
	Args：
		object:发布的对象
		version：指定需要发布的版本信息
	
	"""
	if dispatchObject(object, version):
		dir_map = loadVersionMap()
		if object in dir_map.keys():
			if cfg.FLAG_DEBUG:
				print((dir_map, object))
			if isExistVersion(dir_map, object, version):
				modVersion(dir_map, object, version)
			else:
				addVersion(dir_map, object, version, flag = False)  #这里是指有object但是没有version
		else:
			addVersion(dir_map, object, version, flag = True)  #这里是连object都没有
		dumpVersionMap(dir_map)
	else:
		print("WARN: Publish ["+ object + "]["+ version +"] failed!")
	
def Publish(args_map):
	"""
	发布版本
	Args:
		args_map:命令行参数映射，key为对象名，val为版本信息
	"""
	for object, version in list(args_map.items()):
		try:
			path = cfg.DEPLOY_PATH_LATEST + cfg.SEP + object
			list_dir = os.listdir(path)
			cur_ver = getCurVersion(object)
		except OSError as e:
			print((traceback.format_exc()))
			info = 'Path[' + path + '] not exist'
			doExit(0, info)

		if len(list_dir) == 0:
			info = path + 'is empty'
			doExit(0, info)
		else:
			if version == cfg.FLAG_BLANK:
				pub_ver = calcVersion(cur_ver, cfg.DEF_VERSION_DELTA)
			elif (version.startswith(cfg.PLUS) or version.startswith(cfg.MINUS)) and isVersion(version[1:]):
				pub_ver = calcVersion(cur_ver, version)
			elif isVersion(version):
				pub_ver = version
			else:
				info = version + ' is invalid'
				doExit(0, info)
			pubVersion(object, pub_ver)

def Roll(args_map):
	"""
	版本回退
	Args:
		args_map:命令行参数映射，key为对象名，val为版本信息
		val 为 "dt=20121011_10" or "ver=1.0.0.0]"or "seq=1"
	"""
	dir_map = loadVersionMap()
	for object, version in list(args_map.items()):
		if not dir_map.get(object):
			info = "get invalid object [" + object + "]"
			doExit(0, info)
		try:
			key, val = version.split(cfg.EQUAL)
		except ValueError as e:
			info = "get invalid input [" + version + "]" + cfg.NEWLINE + \
			"    you can use [" + cfg.VL_KEY_DATETIME + "=20121011_10]"+ cfg.NEWLINE + \
			"             OR [" + cfg.VL_KEY_VERSION  + "=1.0.0.0]"+ cfg.NEWLINE + \
			"             OR [" + cfg.VL_KEY_SEQUENCE + "=1]"
			doExit(0, info)
		key = key.strip()
		val = val.strip()
		if key == cfg.VL_KEY_SEQUENCE:
			seqno = string.atoi(val, 10) + 1
			if seqno > 1 and seqno < len(dir_map[object]):  # valid
				version = dir_map[object][seqno][cfg.VL_VERSION_COL]
			else :	#invalid
				info = "get invalid seqno [" + object + "][" + key + "]["+ val + "]"
				doExit(0, info)
		elif key == cfg.VL_KEY_DATETIME:
			version = ""
			for record in dir_map[object][1:]:
				if cmp(record[cfg.VL_DATETIME_COL], val) <= 0:
					version = record[cfg.VL_VERSION_COL]
					break;
				elif cmp(record[cfg.VL_DATETIME_COL], val) > 0:
					continue
			if version == "":
				print(("version not found [" + object + "][" + key + "]<=["+ val + "]"))
		elif key == cfg.VL_KEY_VERSION:
			version = val
		else:
			info = "get invalid input [" + key + "]" + cfg.NEWLINE + "    you can use [" + cfg.VL_KEY_SEQUENCE + cfg.SEP_COMM +	cfg.VL_KEY_DATETIME + cfg.SEP_COMM + cfg.VL_KEY_VERSION	+ "]"
			doExit(0, info)
		if isExistVersion(dir_map, object, version):
			modVersion(dir_map, object, version)
		else:
			info = object + " Version[" + version + "] not found"
			doExit(0, info)
	dumpVersionMap(dir_map)

def isVersion(args):
	"""
	判断参数是否为合法的版本号格式
	合法的版本号格式为'^\d+(\.\d+)*$'
	"""
	m = re.match(cfg.RE_VERSION,args)
	if m is not None:
		return True
	else:
		return False

def showVersionList():
	"""
	根据version.list，将所有对象以及对应的所有版本信息输出
	"""
	dir_map = loadVersionMap()
	showVersion(dir_map)

def showVersion(dir_map):
	"""
	获取version.list列表
	"""
	for object in list(dir_map.keys()):
		showObjectVersion(dir_map, object, cfg.FLAG_BLANK)

def showObjectVersion(dir_map, object, version):
	"""
	根据version.list，将object的对应version状态输出
	"""
	record_list = dir_map[object]

	print('------------------------------------------------------------')
	print(('OBJECT:[' + object + "]"))
	print(('%03s\t%-8s\t%16s\t%2s'%('SEQ',record_list[0][cfg.VL_VERSION_COL], record_list[0][cfg.VL_DATETIME_COL],record_list[0][cfg.VL_STATUS_COL])))

	n = len(record_list)
	if isVersion(version):
		##
		for i in range(1, n):
			if record_list[i][cfg.VL_VERSION_COL] == version:
				print(('%03s\t%-8s\t%16s\t%2s'%((str(i-1)) if (i-1)>0 else '*',record_list[i][cfg.VL_VERSION_COL], record_list[i][cfg.VL_DATETIME_COL],record_list[i][cfg.VL_STATUS_COL])))
	else:
		if version != " " :
			rec_num = int(version) + 1
			if n > rec_num :
				n = rec_num
		for i in range(1, n):
			print(('%03s\t%-8s\t%16s\t%2s'%((str(i-1)) if (i-1)>0 else '*',record_list[i][cfg.VL_VERSION_COL], record_list[i][cfg.VL_DATETIME_COL],record_list[i][cfg.VL_STATUS_COL])))

def Show(args_map):
	"""
	获得当前版本信息
	Args:
		args_map：命令行参数映射
	"""
	dir_map = loadVersionMap()
	for object, version in list(args_map.items()):
		if isVersion(version) or version.isdigit():
			showObjectVersion(dir_map, object, version)
		else:
			info = 'Version[' + version + '] is invalid'
			doExit(0, info)

def dropVersion(object, version):
	"""
	删除object对应的version，并修改version.list
	"""
	dir_map = loadVersionMap()
	if isExistVersion(dir_map, object, version):
		if dropObjectVersion(dir_map, object, version):
			dumpVersionMap(dir_map)
	else:
		info = 'Object[' + object + '] Version[' + version + '] not found'
		print(info)
		return False

def Drop(args_map):
	"""
	删除版本
	Args:
		args_map:命令行参数映射，key为对象名，val为版本信息
	"""
	for object, version in list(args_map.items()):
		lock.acquire()
		try:
			if not isVersion(version):
				info = 'Version[' + version + '] is invalid'
				print(info)
				continue
			if dropVersion(object, version):
				dropObject(object, version)
		except Exception:
			print((traceback.format_exc()))
		finally:
			lock.release()

def explainArgs(args):
	"""
	解析命令行参数
	verConntrol的参数形式为：--cmd publish... --args "server:ver=version;xml:version"
	Args:
		args的格式：
			publish/drop/show："server，client:1.0.0.0:;xml:0.0.0"  or "all:0.0.0"
			roll:"server:ver=version;xml:version"  or "all:ver=0.0.0" or "server:dt=20121011_10" or "server:seq=1"
	"""
	args_map = {}
	try:
		args_list = args.strip().split(cfg.SEMICOLON)
		for token in args_list:
			if token.find(cfg.COLON) >= 0:
				key, val = token.strip().split(cfg.COLON)
				objects = key.strip().split(cfg.COMMA)
				val = val.strip()
				for object in objects:
					object = object.strip()
					args_map[object] = val
			else:
				objects = token.strip().split(cfg.COMMA)
				for object in objects:
					object = object.strip()
					args_map[object] = cfg.FLAG_BLANK
		if args_map.get('all'):
			dir_map = loadVersionMap()
			object_list = list(dir_map.keys())
			for object_name in object_list:
				args_map[object_name] = args_map['all']
			del args_map['all']

	except Exception as e:
		print((traceback.format_exc()))
		info = 'args explain failed'
		doExit(0, info)
	else:
		return args_map

def verControl(**option):
	"""
	管理版本的主方法
	Args：
		option：命令行参数映射
	"""
	if not option.get(cfg.ARGS):
		showVersionList()
		info = 'has no args'
		doExit(0, info)
	##dir_map = loadVersionMap() 全局变量 只load一次
	args_map = explainArgs(option[cfg.ARGS])
	try:
		if option[cfg.CMD] == cfg.CMD_VC_PUB :
			Publish(args_map)
		elif option[cfg.CMD] == cfg.CMD_VC_SHOW:
			Show(args_map)
		elif option[cfg.CMD] == cfg.CMD_VC_DROP:
			Drop(args_map)
		elif option[cfg.CMD] == cfg.CMD_VC_ROLL:
			Roll(args_map)
		else:
			Usage()
	except Exception as e:
		print((traceback.format_exc()))
		info = 'please give right args'
		doExit(0, info)

if __name__ == '__main__':
	Dic_Run = {}
	opts, args = getopt.getopt(sys.argv[1:],'r:v::',['cmd=', 'args='])
	for op, value in opts:
		op = op.replace(cfg.DMINUS, cfg.FLAG_NULL)
		Dic_Run[op] = value

	verControl(**Dic_Run)