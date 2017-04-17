#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2016 by chen.xh.
:license:BSD.
"""
import os
import sys
import traceback

from tools import delFilepath
import config as cfg

try:
	import paramiko

	FLAG_SSH = cfg.FLAG_SSH_PARA
	def ssh_conn(ip, port, user, case, args):
		"""
		ssh连接
		Args:
			ip:target IP
			case:
				 cfg.SSH_CASE_KEY:以密钥方式连接
				 cfg.SSH_CASE_PSWD：以密码方式连接
			args:如果以密钥方式连接，该参数为密钥文件
				如果以密码方式连接，则该参数为密码
				
		returns:
			连接成功则返回0和ssh
			连接失败则返回1和ssh
		"""
		try:
			paramiko.util.log_to_file(cfg.FILE_SSH_LOG)
			ssh = paramiko.SSHClient()
			ssh.load_system_host_keys()		##load known_hosts
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

			if case == cfg.SSH_CASE_KEY:
				###？？？
				keyfile = args.strip()
				ssh.connect(ip, port, user, key_filename=keyfile)
			elif case == cfg.SSH_CASE_PSWD:
				pswd = args.strip()
				ssh.connect(ip, port, user, pswd, compress=True)
			return cfg.CMD_SUCC, ssh
		except Exception:
			if cfg.FLAG_DEBUG:
				print(traceback.format_exc())
			return cfg.CMD_FAIL, ssh

	def ssh_exec(ssh, cmd_list, case=cfg.SSH_CASE_IGN):
		"""
		执行远程指令
		Args:
			ssh:ssh连接
			cmd_list：需要执行的指令列表
			case：
				cfg.SSH_CASE_IGN,默认忽略返回值
				cfg.SSH_CASE_NIGN,返回执行指令的输出
		returns:
			当 case=cfg.SSH_CASE_NIGN 返回执行指令的输出
			成功则返回0, out, err
			失败则返回1, out, err
		"""
		info_out = cfg.FLAG_NULL
		info_err = cfg.FLAG_NULL

		for cmd in cmd_list:
			try:
				stdin, stdout, stderr = ssh.exec_command(cmd, timeout=cfg.SSH_TIMEOUT)
				out = stdout.read()
				err = stderr.read()
				info_out += out
				info_err += err
				if case != cfg.SSH_CASE_IGN and len(err) > 0:
					return cfg.CMD_FAIL, info_out, info_err
			except Exception:
				if cfg.FLAG_DEBUG:
					print(traceback.format_exc())
				
				if case == cfg.SSH_CASE_IGN:
					continue
				else:
					return cfg.CMD_FAIL, info_out, info_err
		return cfg.CMD_SUCC, info_out, info_err

	def ssh_opensftp(ssh):
		return ssh.open_sftp()

	def ssh_openshell(ssh):
		return ssh.invoke_shell()

	def ssh_closeshell(shell):
		return shell.close()

	def ssh_close(ssh):
		return ssh.close()

	def ssh_interactive(shell):
		return interactive_shell(shell)

	def sftp_put(sftp, dst, src):
		"""
		执行远程文件拷贝
		
		"""
		try:
			sftp.put(src, dst)
			return cfg.CMD_SUCC
		except Exception:
			if cfg.FLAG_DEBUG:
				print(traceback.format_exc())
			return cfg.CMD_FAIL
	def sftp_puts(sftp, dst_path, *args):
		"""
		给定目的路径，
		"""
		try:
			for src in args:
				dst = dst_path + cfg.SEP_COMM + os.path.basename(src)
				print("SCP %s to %s"%(src, dst) )
				sftp.put(src, dst)
			return cfg.CMD_SUCC
		except Exception:
			return cfg.CMD_FAIL
	
	def sftp_get(sftp, src, dst):
		try:
			sftp.get(src, dst)
			return cfg.CMD_SUCC
		except Exception:
			print(traceback.format_exc())
			return cfg.CMD_FAIL

except ImportError:
	FLAG_SSH = cfg.FLAG_SSH_ORIG

	def readFile(filename):
		with open(filename, 'r') as f:
			return f.read()

	def ssh_exec(ip, cmd_list, case=cfg.SSH_CASE_IGN):
		info_out = cfg.FLAG_NULL
		info_err = cfg.FLAG_NULL
		output = 'out.' + cfg.PID
		for cmd in cmd_list:
			## remove output
			delFilepath(output)
			cmdline = 'ssh -n %s -o ConnectTimeout=%d "%s" >%s'%(ip, cfg.SSH_TIMEOUT, cmd, output)
			try:
				if cfg.FLAG_DEBUG:
					print(cmdline)
				ret = os.system(cmdline)
				ret >>= 8
				if ret == 0:
					info_out += readFile(output)
				else:
					info_err += readFile(output)
				if cfg.FLAG_DEBUG:
					print(('RTN:' + str(ret) + '\nOUT:' + info_out + 'ERR:' + info_err))
				if case != cfg.SSH_CASE_IGN and ret != 0:
					return cfg.CMD_FAIL, info_out, info_err
			except Exception as e:
				if cfg.FLAG_DEBUG:
					print(traceback.format_exc())
				if case == cfg.SSH_CASE_IGN:
					continue
				else:
					return cfg.CMD_FAIL, info_out, info_err
			finally:
				## remove output
				delFilepath(output)
		return cfg.CMD_SUCC, info_out, info_err

	def sftp_put(ip, dst, src):
		try:
#			sftp.put(src, dst)
			cmdline = 'scp -rp -o ConnectTimeout=%d "%s" %s:"%s" >/dev/null 2>&1'%(cfg.SSH_TIMEOUT, src, ip, dst)
			ret = os.system(cmdline)
			ret >>= 8
			return cfg.CMD_SUCC
		except Exception:
			if cfg.FLAG_DEBUG:
				print(traceback.format_exc())
			return cfg.CMD_FAIL
			
	def sftp_puts(ip, dst_path, *args):
		try:
			for src in args:
				dst = dst_path + cfg.SEP_COMM + os.path.basename(src)
				print(("SCP %s to %s"%(src, dst) ))
				cmdline = 'scp -rp -o ConnectTimeout=%d "%s" %s:"%s" >/dev/null 2>&1'%(cfg.SSH_TIMEOUT, src, ip, dst)
				ret = os.system(cmdline)
				ret >>= 8
			return cfg.CMD_SUCC
		except Exception:
			return cfg.CMD_FAIL

	def sftp_get(ip, src, dst):
		try:
			cmdline = 'scp -rp -o ConnectTimeout=%d %s:"%s" "%s" >/dev/null 2>&1'%(cfg.SSH_TIMEOUT, ip, src, dst)
			ret = os.system(cmdline)
			ret >>= 8
			return cfg.CMD_SUCC
		except Exception:
			return cfg.CMD_FAIL
