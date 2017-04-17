#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
:copyright: (c) 2016 by chen.xh.
:license:BSD.
"""

import sys
import os
import re
import zipfile
import hashlib
import shutil
import time
import traceback
import pickle

import config as cfg

if cfg.PY_VER >= '3':
	import queue as Queue
else:
	import Queue

def logout(args):
	"""
	write log to files
	Args:
		args:
			attr log:attr, value
			evevnt log:name, level, msg
	"""
	## ATTR='...' ATTRVALUE='...'
	## ENAME='...' ELEVEL='1~5' ...
	timestamp = time.strftime('%b %d %H:%M:%S')
	outstr = ("%s %s %s 0[%s]: "%(timestamp, cfg.HOSTNAME, cfg.WORK_DIR, cfg.PID))

	if len(args) == 2:
		outstr = outstr + cfg.FLAG_BLANK.join(args)
	else:
		outstr = outstr + 'event ' + cfg.FLAG_BLANK.join(args)
	if path_exist(cfg.FILE_SYSLOG):
		with open(cfg.FILE_SYSLOG, 'a+') as f:
			f.write(outstr + cfg.NEWLINE)

def logAttr(attr, value):
	"""
	write attr log
	"""
	logout([attr, value])

def logEvent(name, level, msg):
	"""
	write event log
	"""
	logout([name, level, msg])

def md5sum(fname):
	"""
	cal MD5 for file
	"""
	def read_chunks(fh):
		fh.seek(0)
		chunk = fh.read(8096)
		while chunk:
			yield chunk
			chunk = fh.read(8096)
		else: #最后要将游标放回文件开头
			fh.seek(0)

	m = hashlib.md5()
	if isinstance(fname, str) and os.path.exists(fname):
		fh = open(fname, "rb")
		for chunk in read_chunks(fh):
			m.update(chunk)
	#上传的文件缓存或已打开的文件流
	elif fname.__class__.__name__ in ["StringIO", "StringO"] or isinstance(fname, file):
		for chunk in read_chunks(fname):
			m.update(chunk)
	else:
		return ""
	return m.hexdigest()

def md5check(fname, md5fname):
	"""
	check md5 in case the file has been tampered with
	"""
	md5fh = open(md5fname, "r")
	return (md5sum(fname) == md5fh.readline())

def doExit(n, info):
	"""
	print error info and exit program 
	"""
	print(info)
	sys.exit(n)

def path_exist(filepath):
	"""
	judge whether a file exists
	"""
	return os.path.exists(os.path.basename(filepath))

def make_dirs(path):
	"""
	if path is not exit and make it
	"""
	if not os.path.exists(path):
		return os.makedirs(path)

def zip_dir(dir_list, zipfilename):
	"""
	recursive zip files and dictionaries
	Args:
		dir_list:
		zipfilename:
	"""
	filelist = []
	flag_regex = False
	for dirname, regex in dir_list:
		if regex:
			flag_regex = True
		if os.path.isfile(dirname):
			filelist.append(dirname)
		else:
			for root, dirs, files in os.walk(dirname):
				for name in files:
					m = re.match(regex, name)
					if m is not None:
						filelist.append(os.path.join(root, name))
				for name in dirs:
					filelist.append(os.path.join(root, name))
	zf = zipfile.ZipFile(zipfilename, "w")
	for tar in filelist:
		if not flag_regex:
			arcname = os.path.basename(dirname) + tar[len(dirname):]
			zf.write(tar, arcname)
		else:
			zf.write(tar,tar)
	zf.close()

def unzip_file(zipfilename, unziptodir):
	"""
	unzip zipfilename to unziptodir
	"""
	unziptodir = unziptodir.replace(cfg.SEP_DCOMM, cfg.SEP_COMM)
	make_dirs(unziptodir)
	zfobj = zipfile.ZipFile(zipfilename)
	for name in zfobj.namelist():
		name = name.replace(cfg.SEP_DCOMM,cfg.SEP_COMM)
		if name.endswith(cfg.SEP_COMM):
			os.makedirs(os.path.join(unziptodir, name))
		else:
			ext_filename = os.path.join(unziptodir, name)
			ext_filename = ext_filename.replace(cfg.SEP_DCOMM,cfg.SEP_COMM)
			ext_dir= os.path.dirname(ext_filename)
			make_dirs(ext_dir)
			outfile = open(ext_filename, 'wb')
			outfile.write(zfobj.read(name))
			outfile.close()

def join_path(base, *args):
	"""
	join args with base successively to a new path
	"""
	filepath = base
	for arg in args:
		filepath = filepath + cfg.SEP_COMM + arg
	filepath = filepath.replace( '//', cfg.SEP_COMM)
	return filepath

def printList(List):
	for item in List:
		print(item)

def delFilepath(filepath):
	try:
		if os.path.isdir(filepath):
			shutil.rmtree(filepath)
		elif os.path.isfile(filepath):
			os.remove(filepath)
		else:
			pass
		return 0
	except Exception as e:
		print(traceback.format_exc())
		return 1

def loadPickle(filepath):
	"""
	load obj form pickle file filepath
	"""
	f = open(filepath, 'rb')
	obj = pickle.load(f)
	f.close()
	return obj

def dumpPickle(obj, filepath):
	"""
	dump obj to pickle file filepath
	"""
	f = open(filepath, 'wb')
	pickle.dump(obj, f, protocol=2)
	f.close()

def isMatchFiles(ver_map):
	"""
	check ver_map and file struct is matched or not
	"""
	path_list = os.listdir(cfg.DEPLOY_PATH_RELEASE)
	key_list = list(ver_map.keys())
	count = 0

	if sorted(path_list) == sorted(key_list):
		for key in key_list:
			version_dirs = os.listdir(cfg.DEPLOY_PATH_RELEASE + cfg.SEP + key)
			version_list = []
			for record in ver_map[key][1:]:
				version_list.append(record[cfg.VL_VERSION_COL])
			if sorted(version_dirs) == sorted(version_list):
				count += 1
			else:
				print("Version NOT match")
				print("--------------------------------------------")
				print(("DIR:" + cfg.NEWLINE))
				print(version_dirs)
				print("--------------------------------------------")
				print(("VL:" + cfg.NEWLINE))
				print(version_list)
	else:
		print("Object NOT match")
		print("--------------------------------------------")
		print(("DIR:" + cfg.NEWLINE))
		print(path_list)
		print("--------------------------------------------")
		print(("VL:" + cfg.NEWLINE))
		print(key_list)
	if count == len(ver_map):
		return True
	else:
		return False

def sortVersion(ver_map):
	"""
	sort ver_map as the second column for the standard
	"""
	for key in list(ver_map.keys()):
		ver_map[key].sort( key=lambda x: x[1], reverse=True)

def readVersionList(filename):
	"""
	read lines from filename saved as a list
	"""
	try:
		lines = []
		if os.path.isfile(filename):
			with open(r''+ filename, 'r') as f:
				lines = f.readlines()
		return lines
	except IOError as e:
		print(traceback.format_exc())
		info = filename + 'can\'t open'
		doExit(0, info)

def loadVersionMap():
	"""
	transfer lines to a map
	"""
	lines = readVersionList(cfg.FILE_VERSION)
	ver_map = {}
	val = []
	flag = False

	for line in lines:
		line = line.strip()
		if line.startswith(cfg.FLAG_TIPS):
			line_list = line.split()
			len_row = len(line_list)
			a_DmnNum = {}
			DOMAIN = cfg.FLAG_NULL

			for i in range(0,len_row):
				DOMAIN = line_list[i]
				a_DmnNum[DOMAIN] = i
			val = line_list
		elif line.startswith(cfg.OPEN_BRACKET):
			left = line.find(cfg.OPEN_BRACKET)
			right = line.find(cfg.CLOSE_BRACKET)
			Name = line[left+1:right].strip()
			ver_map[Name] = []
			ver_map[Name].append(val[1:])
		elif not line:
			continue
		else:
			line_list = line.split()
			ver_map[Name].append(line_list)
	sortVersion(ver_map)
	return ver_map

def writeVersionList(filename, newlines):
	"""
	write newlines to filename
	"""
	try:
		with open(filename, 'w') as f:
			f.writelines(newlines)
	except IOError as e:
		print((traceback.format_exc()))
		info = filename + ' can\'t open'
		doExit(0, info)

def dumpVersionMap(ver_map):
	"""
	transfer ver_map to lines and write lines to version.list
	Arge:
		ver_map:a map like object：version and status analysis from version.list
	"""
	lines = []
	flag = False
	for key in list(ver_map.keys()):
		if not flag:	#
			content = cfg.FLAG_TIPS + cfg.FLAG_BLANK + cfg.FLAG_BLANK.join(ver_map[key][0]) + cfg.NEWLINE
			lines.append(content)
			flag = True

		lines.append('['+key+']' + cfg.NEWLINE)
		i = 0
		for val in ver_map[key]:
			i = i + 1
			if i > 1:
				content = cfg.FLAG_BLANK.join(val)
				lines.append(content + cfg.NEWLINE)
	writeVersionList(cfg.FILE_VERSION, lines)

def getObjectPath(object):
	"""
	获取发布对象的路径
	Args:
		object:server or client or xml
	Returns:
		/relese/object/version/ 即对象的当前版本的目录
	"""
	objectPath = cfg.FLAG_NULL
	ver_map = loadVersionMap()
	isMatchFiles(ver_map)
	record_list = ver_map[object]
	if len(record_list) > 1:
		cur_ver = record_list[1][cfg.VL_VERSION_COL]
		objectPath = cfg.DEPLOY_PATH_RELEASE + cfg.SEP_COMM + object + cfg.SEP_COMM + cur_ver
	return objectPath

class StructError(Exception):
	"""
	version.list 的结构与/release/目录结构不匹配引发的异常
	"""
	pass

