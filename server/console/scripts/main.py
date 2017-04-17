#!/usr/bin/python
# -*- coding: utf-8	-*-

"""
应用服务的版本管理主函数
"""
import os
import sys
import getopt

import config as cfg

if __name__ == '__main__':
	if cmp(cfg.PY_VER, "2.6.0") < 0:
		print("%s python version[%s] is too old!"%(cfg.HOSTNAME, cfg.PY_VER))
		sys.exit(1)
	else:
		from ecall import Ecall
	
	Dic_Run = {}
	opts, args = getopt.getopt(sys.argv[1:], cfg.OPTION_OPTS, cfg.OPTION_ARGS)
	for op, value in opts:
		op = op.replace(cfg.DMINUS, '')
		Dic_Run[op] = value
	
	Ecall(**Dic_Run)
#verControl	 --cmd verControl --args publish,client:1.8.1.2;...
