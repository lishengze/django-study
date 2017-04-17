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

for filename in os.listdir(cfg.WORK_BASE):
	m = re.match("%s|%s"%(cfg.REGEX_CONSOLEZIP,cfg.REGEX_OPTMAP), filename)
	if (m is not None): 
		delFilepath(filename)


