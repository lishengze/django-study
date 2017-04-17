#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
define global variable
:copyright: (c) 2016 by chen.xh.
:license:BSD.
"""
CONSOLE_VERSION='1.0.0'

import os
import sys
import platform
import socket

sys.path.append(os.path.abspath('.'))


DAEMON_IP = '172.1.128.170'
DAEMON_PORT = 18888

USER = 'test'
USER_PSWD = 'shanghai'

FLAG_DEBUG = False
WORK_DIR = 'console'
WORK_BIN = 'bin'
WORK_CFG = 'config'
WORK_SCR = 'scripts'
WORK_SHELL = 'shell'
WORK_PACKAGE = 'packages'
WORK_MODULES = 'modules'
WORK_LOG = 'log'
WORK_TEMP = 'temp'
WORK_FLOW = 'flow'
WORK_UPDATE = 'update'
WORK_TASK = 'task'

SYS_WINDOWS = 'Windows'
SYS_WIN = 'Win'
SYS_LINUX = 'Linux'

def getPythonVersion():
	return platform.python_version()

def getSystem():
	return platform.system()

def getArch():
	ArchInfo = platform.architecture()[0]
	return ArchInfo.replace('bit', '')

def getOSType():
	Sys = getSystem()
	if Sys == SYS_WINDOWS:
		Sys = SYS_WIN
	return Sys.lower() + getArch()

def getOSTypeFromStr(osinfo):
	Sys, ArchInfo = osinfo.split(';')
	if Sys == SYS_WINDOWS:
		Sys	= SYS_WIN
	return Sys.lower() + ArchInfo.replace('bit', '')

SYSTEM = getSystem()
OS_TYPE = getOSType()
PY_VER = getPythonVersion()
PID = str(os.getpid())
HOSTNAME = socket.gethostname()

SYSTEM_LINUX = 'linux64'
SYSTEM_WIN = 'win64'

if SYSTEM == SYS_WINDOWS:
	HOME = os.getenv('HOMEDRIVE') + os.getenv('HOMEPATH')# + SEP +'Desktop'
else:
	HOME = os.getenv('HOME')

SSH_PORT = 22
SSH_KEY = HOME + '/.ssh/id_rsa'
SSH_CASE_KEY = 0
SSH_CASE_PSWD = 1
SSH_CASE_IGN = 0
SSH_CASE_NIGN = 1
SSH_TIMEOUT = 30
SSH_THREADS = 10

FLAG_TREADPOOL = True

FLAG_TASK_READY = 1
FLAG_TASK_START = 2
FLAG_TASK_END = 3

FLAG_SRV_UNKNOWN = 0
FLAG_SRV_UNDEPLOY = 1
FLAG_SRV_ALIVE = 2
FLAG_SRV_NOTALIVE = 3

TIMEOUT_SRV_STATUS = 60*10
TIMEOUT_SCHDL_TASK = 60*60*12
TIMEOUT_TASK_RESULT = 60*60*12*3

TIP_HEAD = '[HEAD]'
TIP_HEAD_FILE = '[FILE]'
TIP_HEAD_UPLOAD = '[UPLOAD]'
TIP_HEAD_FREQ = '[FREQ]'
TIP_HEAD_FRSP = '[FRSP]'
TIP_HEAD_REQ = '[REQ]'
TIP_HEAD_RSP = '[RSP]'
TIP_HEAD_NTF = '[NTF]'
TIP_HEAD_RPC = '[RPC]'
TIP_INFO_EOF = '[EOF]'
TIP_HEAD_SRVINFO = '[SRV_INFO]'
TIP_INFO_TASK = '[TASK]'
TIP_BODY_REQ = '[REQBODY]'
TIP_BODY_RSP = '[RSPBODY]'
TIP_BODY_VERINFO = '[VERINFO]'
TIP_RESULT_START = '[RESULT]<<<'
TIP_RESULT_END = '[RESULT]>>>'

TASK_TYPE_ECALL = 1
TASK_TYPE_VERCONTROL = 2
TASK_TYPE_PYTHON = 0

FLAG_REQTYPE_TASKINFO = 0
FLAG_REQTYPE_TASKRESULT = 1
FLAG_REQTYPE_TASKLIST = 2
FLAG_REQTYPE_SRVSTATUS = 3
FLAG_REQTYPE_VERSION = 4

FLAG_SSH_ORIG = 0
FLAG_SSH_PARA = 1

EXEC_ALL = 0
##target IP exec
EXEC_TGT = 1
EXEC_RELAY = 2

ELEVEL_FATAL = '1'
ELEVEL_ERROR = '2'
ELEVEL_WARN = '3'
ELEVEL_NOTIFY = '4'
ELEVEL_INFO = '5'
ELEVEL_DEBUG = '6'

EQUAL = '='
PLUS = '+'
MINUS = '-'
COMMA = ','
DOT = '.'
POUND = '#'
DASH = '~'
COLON = ':'
DCOLON = '::'
SQUOTE = "'"
DQUOTE = '"'
SEMICOLON = ';'
EXCLAMATION = '!'
OPEN_BRACKET = '['
CLOSE_BRACKET = ']'
OPEN_PAREN = '('
CLOSE_PAREN = ')'
SEP = os.sep
SEP_COMM = '/'
SEP_DCOMM = '\\'
NEWLINE = os.linesep
FLAG_NULL = ''
FLAG_BLANK = ' '
FLAG_ARGS = '@'
FLAG_TIPS = '@@'
FLAG_TAB = '\t'
DMINUS = '--'

CMD = 'cmd'
SUFF_CMD = 'Cmd'
CTR = 'ctr'
SRV = 'srv'
SRVNO = 'srvno'
GRP = 'grp'
OPT = 'opt'
OS = 'os'
IOS = 'ios'
ICTR = 'ictr'
ISRV = 'isrv'
ISRVNO = 'isrvno'
IOPT = 'iopt'
ARGS = 'args'
ZIPF = 'zipfile'
RELAY = 'relay'
ALL = 'all'
TID = 'tid'
SRC = 'src'
DST = 'dst'
REGEX_CONSOLEZIP = '^' + WORK_DIR + '.zip.*'
REGEX_OPTMAP = '^opt_map.*'

CMD_SUCC = 0
CMD_FAIL = 1

CMD_SUCC_TIP = 'SUCC'
CMD_FAIL_TIP = 'FAILED'
CMD_CONNERR_TIP = 'Conn err'
CMD_UNDEPLOY_TIP = 'Path Not found'
CMD_NOALIVE_TIP = 'App Not run'
CMD_RUNNING_TIP = 'Already running'
CMD_STOPPED_TIP = 'App stopped'

CMD_DEPLOYCONSOLE = 'deployConsole'
CMD_UNDEPLOYCONSOLE = 'undeployConsole'
CMD_DEPLOYSERVER = 'deployServer'
CMD_UNDEPLOYSERVER = 'undeployServer'
CMD_REDEPLOYSERVER = 'redeployServer'
CMD_COPYXML = 'copyXml'
CMD_STOPCLN = 'stopcln'
CMD_START = 'start'
CMD_RUN = 'run'
CMD_RUN_R = 'run_r'
CMD_PUT = 'put'
CMD_GET = 'get'
CMD_ZIP = 'zip'
CMD_EXECCMD = 'execCmd'

CMDS_HOSTLEVEL = (CMD_DEPLOYCONSOLE, CMD_UNDEPLOYCONSOLE, CMD_RUN, CMD_RUN_R, CMD_PUT, CMD_GET)
CMDS_DEPLOY = (CMD_DEPLOYCONSOLE, CMD_UNDEPLOYCONSOLE, CMD_DEPLOYSERVER, CMD_UNDEPLOYSERVER, CMD_REDEPLOYSERVER, CMD_COPYXML)

CMD_INFO = 'info'
CMDS_BASE = 'run, run_r, put, get'
CMDS_APP_BASE = "start, stop, show, alive, restart"
CMDS_APP = CMDS_APP_BASE + ', ' + 'clean, stopcln, version'
CMDS_TOP = COMMA.join(CMDS_DEPLOY) + COMMA + CMDS_APP + COMMA + CMDS_BASE

OPTION_OPTS = 'r:v::'
OPTION_ARGS = ['cmd=', 'ctr=','srv=','srvno=','grp=', 'opt=', 'ictr=', 'os=', 'ios=', \
		 'isrv=', 'isrvno=', 'iopt=', 'args=', 'file=', 'ip=', 'cmd2=', 'tid=', 'src=', 'dst=']

SERVER = 'server'
CLIENT = 'client'
XML = 'xml'
XML_CONFIG = 'config'
XML_SRVNAME = 'monmanager'
XML_SRVS = {XML_CONFIG : (XML_SRVNAME,)}

WORK_BACKUP = "pkg_backup"
WORK_FILES = "pkg_files"

WORK_BASE = HOME
WORK_PATH = WORK_BASE + SEP + WORK_DIR
###添加存放update服务的目录
WORK_PATH_UPDATE = WORK_PATH + SEP + WORK_UPDATE
WORK_PATH_UPDATE_BAK = WORK_PATH_UPDATE + SEP + WORK_BACKUP
WORK_PATH_UPDATE_TEMP = WORK_PATH + SEP + WORK_UPDATE + SEP + WORK_TEMP
WORK_PATH_BIN = WORK_PATH + SEP + WORK_BIN
WORK_PATH_CFG = WORK_PATH + SEP + WORK_CFG
WORK_PATH_SCR = WORK_PATH + SEP + WORK_SCR
WORK_PATH_SHELL = WORK_PATH + SEP + WORK_SHELL
WORK_PATH_PACKAGE = WORK_PATH + SEP + WORK_PACKAGE
WORK_PATH_MODULES = WORK_PATH + SEP + WORK_MODULES
WORK_PATH_LOG = WORK_PATH + SEP + WORK_LOG
WORK_PATH_TEMP = WORK_PATH + SEP + WORK_TEMP
WORK_PATH_TASK = WORK_PATH + SEP + WORK_TASK


DEPLOY_DIR = 'app'
##[主控]最新的发布文件
DEPLOY_LATEST = 'latest'
##[主控]版本仓库
DEPLOY_RELEASE = 'release'
##[受控]服务运行目录
DEPLOY_RUN = 'run'
##[受控]服务发布缓存目录
DEPLOY_UPDATE = 'update'

DEPLOY_PATH = WORK_BASE + SEP + DEPLOY_DIR
DEPLOY_PATH_LATEST = DEPLOY_PATH + SEP + DEPLOY_LATEST
DEPLOY_PATH_RELEASE = DEPLOY_PATH + SEP + DEPLOY_RELEASE
DEPLOY_PATH_UPDATE = DEPLOY_PATH + SEP + DEPLOY_UPDATE
DEPLOY_PATH_RUN = DEPLOY_PATH + SEP + DEPLOY_RUN

DEPLOY_PATH_SERVER_LINUX = DEPLOY_PATH_LATEST + SEP + SERVER +  SEP + SYSTEM_LINUX
DEPLOY_PATH_CLIENT_LINUX = DEPLOY_PATH_LATEST + SEP + CLIENT +  SEP + SYSTEM_LINUX
DEPLOY_PATH_XML_LINUX = DEPLOY_PATH_LATEST + SEP + XML +  SEP + SYSTEM_LINUX
FILE_SUF_BAT = '.bat'
FILE_SUF_SHELL = '.sh'
FILE_SUF_MD5 = '.md5'
FILE_SUF_ZIP = '.zip'
FILE_SUF_LIST = '.list'
FILE_SUF_LOG = '.log'
FILE_SUF_SCR = '.py'
FILE_SUF_LINUX = '.linux'
FILE_SUF_TZ= '.tz'
FILE_SUF_RPM= '.rpm'

FILE_NAME_SERVICE ='service.list'
FILE_NAME_START = 'start.list'
FILE_NAME_HOSTS = 'hosts.list'
FILE_NAME_RELAY = 'relay.list'
FILE_NAME_USER = 'user.list'
FILE_NAME_CONSOLE = 'console.list'
FILE_NAME_MENU = 'console.menu'
FILE_NAME_DC = 'datacenter.list'
FILE_NAME_USER = 'user.list'
FILE_NAME_VERSION = 'version.list'
FILE_NAME_SYSLOG = 'Syslog.log'
FILE_NAME_OPTLOG = 'Operation.log'
FILE_NAME_SHLLOG = 'shell.log'
FILE_NAME_CMDLOG = 'command.log'
FILE_NAME_SRVCTRL = 'srvControl.py'
FILE_NAME_VERCTRL = 'verControl.py'
FILE_NAME_DAEMON = 'task_daemon.py'
FILE_NAME_MAIN = 'main.py'
FILE_NAME_UPDATE = 'do_update.py'

FILE_NAME_PKGZIP = WORK_DIR + DOT + PID + FILE_SUF_ZIP
FILE_NAME_TRANSZIP = 'transfer' + DOT + PID + FILE_SUF_ZIP

if SYSTEM == SYS_WINDOWS:
	FILE_NAME_INSTALL = 'install' + FILE_SUF_BAT
	FILE_NAME_APPCTRL = 'appctrl' + FILE_SUF_BAT
else:
	FILE_NAME_INSTALL = 'install' + FILE_SUF_SHELL
	FILE_NAME_APPCTRL = 'appctrl' + FILE_SUF_SHELL

FILE_START =  WORK_PATH_CFG + SEP + FILE_NAME_START
FILE_SERVICE = WORK_PATH_CFG + SEP + FILE_NAME_SERVICE
FILE_HOSTS = WORK_PATH_CFG + SEP + FILE_NAME_HOSTS
FILE_RELAY = WORK_PATH_CFG + SEP + FILE_NAME_RELAY
FILE_VERSION = DEPLOY_PATH_RELEASE + SEP + FILE_NAME_VERSION

FILE_START_TEMP = WORK_PATH_TEMP + SEP + 'start.' + PID
FILE_SERVICE_TEMP = WORK_PATH_TEMP + SEP +'service.' + PID
FILE_OBJS = WORK_PATH_TEMP + SEP + 'object.' + PID

FILE_SSH_LOG = WORK_PATH_LOG + SEP + 'paramiko.log'
FILE_SYSLOG = WORK_PATH_LOG + SEP + FILE_NAME_SYSLOG
FILE_APPCTRL = WORK_PATH_SHELL + SEP + FILE_NAME_APPCTRL
FILE_DAEMON_IN = '/dev/null'
FILE_DAEMON_OUT = WORK_PATH_LOG + SEP + 'daemon_out.log'
FILE_DAEMON_ERR = WORK_PATH_LOG + SEP + 'daemon_err.log'
FILE_DAEMON_TASKOUT = WORK_PATH_LOG + SEP + 'task.log'
FILE_DAEMON_MAINPID = WORK_PATH_TEMP + SEP + 'daemon_main.pid'
FILE_DAEMON_SUBPID = WORK_PATH_TEMP + SEP + 'daemon_sub.pid'
FILE_PROCESSING = WORK_PATH_LOG + SEP + 'processing.log.' + PID

FILE_DAEMON_TASK_LIST =  WORK_PATH_TEMP + SEP + '.daemon_task_list.pk'

FILE_LISTS_CFG = [(WORK_DIR + r"/config/", "^\w*%s$"%(FILE_SUF_LIST))]
FILE_LISTS_SCR = [
	(WORK_DIR + r"/shell/", "^.*%s$"%(FILE_SUF_BAT)),
	(WORK_DIR + r"/shell/", "^.*%s$"%(FILE_SUF_SHELL)),
	(WORK_DIR + r"/scripts/", "^.*%s$"%(FILE_SUF_SCR))
]
FILE_LISTS_PKG = [
	(WORK_DIR + r"/packages/", "^.*%s$"%(FILE_SUF_TZ)),
	(WORK_DIR + r"/packages/", "^.*%s$"%(FILE_SUF_RPM))
]
FILE_LISTS_MDL = [(WORK_DIR + r"/modules/", '\S')]
FILE_LISTS_WEB = [(WORK_DIR + r"/website/mysite/blog/", "^.*%s$"%(FILE_SUF_SCR))]

FILE_LISTS_ALL = FILE_LISTS_CFG + FILE_LISTS_SCR + FILE_LISTS_PKG + FILE_LISTS_MDL + FILE_LISTS_WEB

DATACENTER = 'DataCenter'
APPNAME = 'AppName'
APPNO = 'AppNO'
FIELD_ARGS = 'Args'
TIP_OSTYPE = 'OSType'

VL_DEL = 'del'

DEF_VERSION_DELTA='+1'
VL_DATETIME='datetime'
VL_VERSION = 'version'
VL_STATUS = 'status'
VL_SEQUENCE = 'sequence'
VL_KEY_SEQUENCE = 'seq'
VL_KEY_DATETIME = 'dt'
VL_KEY_VERSION = 'ver'
VL_VERSION_COL = 0
VL_DATETIME_COL = 1
VL_STATUS_COL = 2
VL_COL_NUM = 3
VL_STATUS_CUR = 'C'
VL_STATUS_HIS = 'H'
VL_STATUS_DEL = 'D'

CMD_VC_PUB = 'publish'
CMD_VC_DROP = 'drop'
CMD_VC_SHOW = 'show'
CMD_VC_ROLL = 'rollback'

RE_VERSION = '^\d+(\.\d+)*$'

DEFAULT_GRP = 'AllServices'
DEFAULT_RECV = 8192

UPDATE_DEL = 'del'
UPDATE_COPY = 'copy'
UPDATE_PUB = 'publish'
UPDATE_CFGFILE = 'update.cfg'

VAL_RESTART = 0
VAL_UNDEPLOY = 1
VAL_DEPLOY = 2
VAL_REDEPLOY = 3

KEY_STOP = 'stop'
KEY_START = 'start'
KEY_DEPLOY = 'deploy'
KEY_REDEPLOY = 'redeploy'
KEY_UNDEPLOY = 'undeploy'