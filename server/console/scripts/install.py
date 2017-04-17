#!/usr/bin/python
# -*- coding: utf-8	-*-

"""
应用服务的安装脚本
"""
import os
import sys
import getopt
import stat

import config as cfg

def makeTempPath():
	mkdirs(cfg.WORK_PATH_TEMP)
	mkdirs(cfg.WORK_PATH_LOG)

def makeAppPath():
	mkdirs(cfg.DEPLOY_PATH_UPDATE)
	mkdirs(cfg.DEPLOY_PATH_RUN)

def chmodExec(dir_list):
	if cfg.SYS_LINUX == cfg.SYSTEM:	
		filelist = []
		for	dirname, regex in dir_list:
			dirpath = cfg.WORK_BASE + cfg.SEP_COMM + dirname
			if os.path.isfile(dirpath):
				filelist.append(dirpath)
			else:
				for	root, dirs, files in os.walk(dirpath):
					for	name in files:
						m = re.match(regex,	name)
						if m is not None:
							filelist.append(os.path.join(root, name))
		for filepath in filelist:
			os.chmod(filepath, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH)

if __name__ == '__main__':
	if cmp(cfg.PY_VER, "2.6.0") < 0:
		print("%s python version[%s] is too old!"%(cfg.HOSTNAME, cfg.PY_VER))
		sys.exit(1)
	else:
		from tools import *
	makeTempPath()
	makeAppPath()
	chmodExec(cfg.FILE_LISTS_SCR)
	