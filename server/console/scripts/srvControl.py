#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2016 by chen.xh.
:license:BSD.
"""
import os
import sys
import shutil
import getopt
import stat
import traceback

from tools import md5check, unzip_file, make_dirs, join_path, delFilepath
import config as cfg

def updateSrv(*args):
	"""
	unzip the zip file for deployserver or copyXml to /app/update/ of remote IP 
	args:
		srv:designate deploy service name like 'monevent'
		zipfilepath:designate source *.zip directory like '/home/test/console/temp/monevent.linux64.zip.21344'
		md5filepath:designate source *.md5 directory like '/home/test/console/temp/monevent.linux64.zip.md5.21344'
		cfg.XML_CONFIG: only for exec 'copyXml' indicate directory like '/home/test/app/update/monevent/config/'

	returns:
		0 indicate succ
		1 indicate failed
	"""
	try:
		back_flag = False
		## check ZIP and MD5
		if not md5check(args[1], args[2]):
			print( "FILE [" + zipfilepath + "] MD5 check error")
			return 1
		## Backup
		if len(args) == 4:
			unzip_path = join_path(cfg.DEPLOY_PATH_UPDATE, args[0])
			dest_path = join_path(unzip_path, args[3])
		elif len(args) == 3:
			dest_path = join_path(cfg.DEPLOY_PATH_UPDATE, args[0])
		if os.path.isdir(dest_path) :
			back_path = dest_path + '_bak.' + cfg.PID
			if not os.path.exists(back_path):
				shutil.move(dest_path, back_path)
				back_flag = True
		## Unzip
		if len(args) == 4:
			print("unzip:" + args[1] + "to" + unzip_path)
			make_dirs(unzip_path)
			unzip_file(args[1], unzip_path)
		elif len(args) == 3:
			print("unzip:" + args[1] + "to" + cfg.DEPLOY_PATH_UPDATE)
			unzip_file(args[1], cfg.DEPLOY_PATH_UPDATE)
	except Exception as e:  ###!!! opt no key
		## Restore
		if back_flag:
			if os.path.isdir(dest_path):
				shutil.rmtree(dest_path)
			shutil.move(back_path, dest_path)
		print(traceback.format_exc())
		return 1
	else:
		## Drop backup
		if back_flag:
			shutil.rmtree(back_path)
		return 0
###！！！
def getFileDic(files_list):
	"""
	gen a dictionary 
	根据不同的需求区分要拷贝的文件，比如给定了中心名和服务编号，则拷贝
	
	args:
	files_list: a file list is relate to deployedservice like "/home/test/app/update/monprobe/bin/monprobe.linux"
	monprobe.linux
	
	returns:a dictionary key is filename like "monprobe.linux" for each element in files_list and \
		val is dictonary with key is all.all or ctr.srvno ctr.all all.srvno and \
		val is file name With an absolute path file name like "/home/test/app/update/monprobe/bin/monprobe.linux"
	"""
	dic_files = {}
	dic_objs = {}

	for filepath in files_list:
		filename = os.path.basename(filepath.strip())
		if not filename or filename.startswith(cfg.POUND):
			continue
		tokens_list = filename.split(cfg.DOT)
		len_tokens = len(tokens_list)
		if len_tokens < 2 or len_tokens > 4:
			print(cfg.FLAG_NULL)
			continue
		file_obj = tokens_list[0] + cfg.DOT + tokens_list[1]
		if dic_files.has_key(file_obj):
			dic_objs = dic_files[file_obj]
		else:
			dic_objs = {}
		if len_tokens == 2:
			obj_type = cfg.ALL + cfg.DOT + cfg.ALL
		elif len_tokens == 3:
			obj_type = tokens_list[2].lower() + cfg.DOT + cfg.ALL
		elif len_tokens == 4:
			obj_type = tokens_list[2].lower() + cfg.DOT + tokens_list[3].lower()

		dic_objs[obj_type] = filepath
		dic_files[file_obj] = dic_objs
	if cfg.FLAG_DEBUG:
		print(dic_files)
	return dic_files

def getFileTupleList(dic_files, ctr, srvno):
	"""
		根据getFileDic得到的字典，以及给定的参数值ctr, srvno，确定要拷贝的文件信息
	/bin/srv.suff.ctr.srvno
	args:
		dic_files:like {'monevent.ini': {'all.all': '/home/test/app/update/monevent/bin/monevent.ini'}, 'monevent.linux': {'all.all': '/home/test/app/update/monevent/bin/monevent.linux'}, 'monevent.xml': {'all.all': '/home/test/app/update/monevent/bin/monevent.xml'}}

	returns:
		a tuple like [('/home/test/app/update/monevent/bin/monevent.ini', 'monevent.ini'), \
			('/home/test/app/update/monevent/bin/monevent.linux', 'monevent'), \
			('/home/test/app/update/monevent/bin/monevent.xml', 'monevent.xml')]
	"""
	file_tuplist = []
	for file_obj in dic_files.keys():
		filepath = cfg.FLAG_NULL
		if dic_files[file_obj].has_key(ctr + cfg.DOT + srvno):
			## ctr.srvno
			filepath = dic_files[file_obj][ctr + cfg.DOT + srvno]
		elif dic_files[file_obj].has_key(cfg.ALL + cfg.DOT + srvno):
			## "all".srvno
			filepath = dic_files[file_obj][cfg.ALL + cfg.DOT + srvno]
		elif dic_files[file_obj].has_key(ctr + cfg.DOT + cfg.ALL):
			## ctr."all"
			filepath = dic_files[file_obj][ctr + cfg.DOT + cfg.ALL]
		elif dic_files[file_obj].has_key(cfg.ALL + cfg.DOT + cfg.ALL):
			## "all"."all"
			filepath = dic_files[file_obj][cfg.ALL + cfg.DOT + cfg.ALL]
		else:
			## no match
			print("SRV[%s.%s][%s] have no match"%(ctr, srvno, file_obj))
			continue
		### matched
		## copy filepath to DST/file_obj
		##print("COPY [%s] to [%s]"%(filepath, file_obj))
		filename = file_obj
		if filename.endswith(cfg.FILE_SUF_LINUX):
			filename = filename[:len(filename) - len(cfg.FILE_SUF_LINUX)]
		file_tuplist.append((filepath, filename))
	if cfg.FLAG_DEBUG:
		print(file_tuplist)
	return file_tuplist

def copyDirs(dir_list, filepath_src, filepath_dst):
	"""
	make directory dir_dst like /home/test/app/run/monevent1/log /home/test/app/run/monevent1/flow \
		/home/test/app/run/monevent1/config /home/test/app/run/monevent1/bin
	
	args:
		dir_list:['/home/test/app/update/monevent/log', '/home/test/app/update/monevent/flow', '/home/test/app/update/monevent/config', '/home/test/app/update/monevent/bin']
		filepath_src:/home/test/app/update/monevent
		filepath_dst:/home/test/app/run/monevent1
	"""
	for dir_path in dir_list:
		dir_dst = join_path(filepath_dst, dir_path[len(filepath_src):])
		print("mkdir %s"%(dir_dst))
		make_dirs(dir_dst)

def copyFiles(file_tuplist, filepath_src, filepath_dst):
	"""
	copy 
	拷贝文件到中继以及目的主机上update目录下
	args:
		file_tuplist:[('/home/test/app/update/monevent/bin/monevent.ini', 'monevent.ini'), \
			('/home/test/app/update/monevent/bin/monevent.linux', 'monevent'), \
			('/home/test/app/update/monevent/bin/monevent.xml', 'monevent.xml')]
		filepath_src:/home/test/app/update/monevent
		filepath_dst:/home/test/app/run/monevent1
		
	returns:
	"""
	for file_src, filename in file_tuplist:
		file_srcpath = os.path.dirname(file_src)
		file_dst = join_path(filepath_dst, file_srcpath[len(filepath_src):], filename)
		if cfg.FLAG_DEBUG:
			print("copy %s %s"%(file_src, file_dst))
		try:
			file_base, ext = os.path.splitext(file_src)
			shutil.copyfile(file_src, file_dst)
			if ext == cfg.FILE_SUF_LINUX:
				os.chmod(file_dst, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH)    ###修改run目录下的执行程序的执行权限
		except IOError:
			print(traceback.format_exc())
			print('copy file failed!please sure you exec stop!')

def getObjectLists(filepath_src):
	"""
	recursion scanning all directories and files in the directory filepath_src
	args:
		filepath_src:the source path like "/home/test/app/update/monslog"
	returns:
		dir_list:all recursion directories in the directory filepath_src like "['/home/test/app/update/monslog/bin', \
		'/home/test/app/update/monslog/config', '/home/test/app/update/monslog/flow', '/home/test/app/update/monslog/log']"
		file_list:all recursion files in the directory filepath_src like "['/home/test/app/update/monslog/bin/monslog.linux', \
		'/home/test/app/update/monslog/bin/monslog.xml']
"
	"""
	dir_list = []
	file_list = []
	for root, dirs, files in os.walk(filepath_src):
		for dir_name in dirs:
			dir_list.append(os.path.join(root, dir_name))
		for file_name in files:
			file_list.append(os.path.join(root, file_name))
	return dir_list, file_list

def deploySrv(*args):
	"""
	copy directories from app/update/ to app/run/
	args:
		srv:
		ctr:
		srvno:
		cfg.XML_CONFIG:only for 'copyXml' and indicate directory app/update/srvname/config/
	
	returns:
		0 indicate succ
		1 indicate failed
		
	Raises:
	"""
	try:
		## 可以去掉小写
		srv = args[0].lower()
		ctr = args[1].lower()

		if len(args) == 3:
			filepath_src = join_path(cfg.DEPLOY_PATH_UPDATE, srv)
			filepath_dst = join_path(cfg.DEPLOY_PATH_RUN, srv+args[2])
		elif len(args) == 4:
			filepath_src = join_path(cfg.DEPLOY_PATH_UPDATE, srv, args[3])
			filepath_dst = join_path(cfg.DEPLOY_PATH_RUN, srv+args[2], args[3])
		##文件夹以及文件均是带绝对路径的
		dir_list, file_list = getObjectLists(filepath_src)
		##
		dic_files = getFileDic(file_list)
		##
		file_tuplist = getFileTupleList(dic_files, ctr, args[2])
		copyDirs(dir_list, filepath_src, filepath_dst)
		copyFiles(file_tuplist, filepath_src, filepath_dst)
	except Exception as e:
		print(traceback.format_exc())
		return 1
	else:
		return 0

def undeploySrv(srv, srvno):
	"""
	delete app/run/srv+srvno/
	args：
		srv, srvno:designate del path /run/srv+srvno/
	returns:
		0:indicate succ
		1:indicate failed
	"""
	print("----------Undeploy %s.%s----------"%(srv, srvno))
	try:
		## 可以去掉小写
		srv = srv.lower()
		filepath_dst = join_path(cfg.DEPLOY_PATH_RUN, srv+srvno)
		delFilepath(filepath_dst)
	except Exception as e:
		print(traceback.format_exc())
		return 1
	else:
		return 0
