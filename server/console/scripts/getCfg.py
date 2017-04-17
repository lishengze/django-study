#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
配置解析相关模块
:copyright: (c) 2016 by chen.xh.
:license:BSD.
"""
import os
import sys
import re
import traceback

import config as cfg


def list_filter(temp_list, keywords, output, group):
	"""
	根据给定的过滤信息，获得过滤后的配置列表信息
	args:
		temp_list:扩展后的列表信息
		keyworks:
		optout:
		group:
	returns:
		
	"""
	flag = False
	is_key_excluded = False
	is_opt_excluded = False
	list_out = [] #存放过滤后的列表信息
	a_map = {}	#存放传递的参数键值对
	b_map = {} #存放排除过滤的参数值
	a_seek = {}	#存放过滤信息
	b_seek = {}
	keywords_list = []
	output_list = []
	keywords = keywords[:len(keywords)-1]
	out = cfg.FLAG_NULL

	keywords_list = keywords.split(cfg.SEMICOLON)
	if output.startswith(cfg.EXCLAMATION):
		is_opt_excluded = True
		output = output[1:]
	output_list = output.split(cfg.COMMA)

	for keyword in keywords_list:
		keyword = keyword.strip()
		if keyword == cfg.FLAG_NULL:
			continue
		key, value = keyword.split(cfg.EQUAL)
		if value.startswith(cfg.EXCLAMATION):
			is_key_excluded = True
			b_map[key] = value[1:]
		else:
			a_map[key] = value

	len_out = len(output_list)
	isize = len(keywords_list)
	iseek = 0
	row = 0

	for line in temp_list:
		line = line.strip()
		imatch = 0
		if not line:
			continue
		elif line.startswith(cfg.FLAG_TIPS):
			pos = line.find(cfg.FLAG_BLANK)
			row_name = line[pos+1:].strip().split()
			len_row = len(row_name)
			a_DmnNum = {}
			DOMAIN = cfg.FLAG_NULL

			for i in range(0,len_row):
				DOMAIN = row_name[i]
				a_DmnNum[DOMAIN] = i
				if DOMAIN in a_map:
					a_seek[i] = a_map[DOMAIN]	 #用于表示过滤那一列的信息
					iseek = iseek + 1
				if DOMAIN in b_map:
					b_seek[i] = b_map[DOMAIN]	#用于排除过滤，是或的关系，只要有一个符合就continue，不要计数

			if len_out > 0:	 #这要求给定参数的格式是outout的字符串必须以‘，’结尾
				icol = []
				for j in range(0,len_out):
					DOMAIN = output_list[j]
					if DOMAIN != cfg.FLAG_NULL and DOMAIN in a_DmnNum:
						icol.append(a_DmnNum[DOMAIN])
		elif line.startswith(cfg.OPEN_BRACKET) and flag:	#处理结束
			break
		elif line.startswith(cfg.OPEN_BRACKET):
			line_group = line[line.find(cfg.OPEN_BRACKET)+1:line.find(cfg.CLOSE_BRACKET)].strip()
			if group == line_group:
				flag = True
		elif len(line.strip().split()) >= len_row and not line.startswith(cfg.POUND):
			### if not group we need,continue
			if (not flag) and group != cfg.FLAG_NULL:
				continue

			restart = False
			line_list = line.strip().split()
			len_list = len(line_list)
			ival = [] #存放排除过滤信息的具体值
			val = []  #存放过滤信息具体值
			#如果有排除过滤的信息，则信息匹配就跳过该行

			#continue只是用于跳出for循环，不能
			for	i in range(0,len_list):
				if is_key_excluded and i in b_seek:
					ival = b_seek[i].split(cfg.COMMA)
					if line_list[i] in ival:
						restart	= True
						break
				if i in a_seek:
					val = a_seek[i].split(cfg.COMMA)
					##--srvno 10-20 
					if a_seek[i].find(cfg.MINUS) != -1:
						left_val, right_val = a_seek[i].split(cfg.MINUS)
						val = range(int(left_val), int(right_val)+1)
						for j in range(len(val)):
							val[j] = str(val[j])

					if line_list[i] in val:
						imatch = imatch + 1

			if restart:
				continue
			line_str = cfg.DOT.join(line_list[:len_row-1])
			i = 0
			while i < len_list:
				if line_list[i].startswith(cfg.FLAG_ARGS):
					line_list[i] = line_list[i].replace(cfg.FLAG_ARGS,line_list[i-1])
				line_str = line_str + cfg.FLAG_TAB + line_list[i] + cfg.FLAG_TAB
				i = i + 1

#			print('[%s] [%d:%d]'%(line,imatch, iseek))
			if imatch == iseek :
				list_out.append(line_str)
				if cfg.FLAG_DEBUG:
					print(line_str)
				if len_out > 0:
					for i in range(0,len_row):
						if is_opt_excluded and (i not in icol):
							if i == len_row-1 and len_list > len_row:
								for j in (len_row,len_list):
									out = out + line_list[j] + cfg.FLAG_BLANK
							else:
								out = out + line_list[i] + cfg.FLAG_BLANK
						elif (not is_opt_excluded) and i in icol:
							if i == len_row-1 and len_list > len_row:
								for j in (len_row,len_list):
									out = out + line_list[j] + cfg.FLAG_BLANK
						else:
								out = out + line_list[i] + cfg.FLAG_BLANK
					out = out + cfg.NEWLINE
	return list_out

def getcfg(FILE, keywords, output, group):
	"""
	用于扩展列表文件，并通过过滤信息获得过滤后的配置列表信息
	Args:
		FILE：service.list or start.list
	"""
	try:
		f = open(FILE)
		line_dir = {}
		temp_list = []	#存放扩展后的列表信息
		group_all = 'all'   #针对service文件没有group
		line_dir[group_all] = []

		while True:
			line = f.readline()
			if not line:	#如果读到文件尾跳出循环
				break
			elif line.startswith(cfg.FLAG_TIPS):
				temp_list.append(line)
			elif line.startswith(cfg.OPEN_BRACKET):
				group_all = line[line.index(cfg.OPEN_BRACKET)+1:line.index(cfg.CLOSE_BRACKET)]	  #服务组名
				line_dir[group_all]= []
			elif line.startswith(cfg.PLUS):	#添加服务
				srv_name = line.strip()[1:]	#添加的服务组名
				for srv in line_dir[srv_name]:
					line_dir[group_all].append(srv)
			elif line.startswith(cfg.MINUS):	#去除服务
				srv_name = line[1:-1].strip()
				for srv in line_dir[srv_name]:
					line_dir[group_all].remove(srv)
			elif (not line.startswith(cfg.POUND)) and len(line.strip().split())>=4:
				line_left = line.find(cfg.OPEN_PAREN)	 #定位左括号和右括号位置
				line_right = line.find(cfg.CLOSE_PAREN)
				if line_left == -1:
					line_dir[group_all].append(line.strip())
				else:
					line_temp = line[line_left+1:line_right]	#取出括号中的内容
					dig_list = line_temp.split(cfg.COMMA)	 #分隔有逗号的服务编号
					len_list = len(dig_list)
					for i in range(0, len_list):
						mid	= dig_list[i].find(cfg.DASH)	#判断每个以逗号分隔的数据是否包含‘~’
						if mid == -1:
							line_add_list = line[:line_left] + dig_list[i] + line[line_right+1:]
							line_dir[group_all].append(line_add_list.strip())
						else:
							left = dig_list[i][:mid]
							right = dig_list[i][mid+1:]
							left = int(left)
							right = int(right)
							for i in range(left, right+1):
								line_add_list= line[:line_left] + str(i) + line[line_right+1:]
								line_dir[group_all].append(line_add_list.strip())
		for key, value in list(line_dir.items()):
			if key != group_all:
				temp_list.append(cfg.OPEN_BRACKET + key + cfg.CLOSE_BRACKET)
			for val in value:
				temp_list.append(val)
	except IOError as e:
		print(traceback.format_exc())
		###!!!此处该返回还是应该退出
		return 1
	else:
		return list_filter(temp_list, keywords, output, group)
	finally:
		f.close()
#	print(temp_list)

def readHostList(filename):
	with open(r'' + filename, 'r') as f:
		lines = f.readlines()
		return lines

def writeHostList(filename,newlines):
	"""
	将最新的IP，ostype, hostname 信息写到host.list
	"""
	with open(filename, 'w') as f:
		f.writelines(newlines)

def loadHostMap():
	"""
	解析host.list,得到每个IP对应的系统类型，以及主机名
	"""
	lines = readHostList(cfg.FILE_HOSTS)
	host_map = {}
	flag = False

	for line in lines:
		line = line.strip()
		if (not line) or line.startswith(cfg.FLAG_TIPS) or line.startswith(cfg.POUND):
			continue
		ip, ostype, hostname = line.split()
		host_map[ip] = (ostype, hostname)
	return host_map

def dumpHostMap(host_map):
	"""
	将host_map写进host.list文件中
	Args:
		host_map[ip] = (ostype, hostname)
		
	"""
	host_map = sortHostMap(host_map)
	lines = ["@@ IpAddr OSType Hostname"+ cfg.NEWLINE + cfg.NEWLINE]
	flag = False

	for ip, key in host_map:
		content = "%s %s %s"%(ip, key[0], key[1])
		lines.append(content + cfg.NEWLINE)
	writeHostList(cfg.FILE_HOSTS, lines)

def sortHostMap(host_map):
	host_map = sorted(list(host_map.items()), key=lambda d:d[0])
	return host_map


def readRelayFile():
	try:
		f = open(cfg.FILE_RELAY)
		lines_list = f.readlines()
		return lines_list
	except Exception as e:
		print((traceback.format_exc()))
	finally:
		f.close()

def loadRelayFile():
	"""
	根据relay.list获得每个IP对应的所有中继IP以及所有后继IP
	"""
	## {ip : relay}
	relay_map = {}
	
	## {ip : [son1, son2, ...]}
	sub_map = {}
	
	## {ip : ([ sons, grandsons, ...])}
	ipsub_map = {}
	
	ip_list = []
	iprelay_map = {}
	lines_list = readRelayFile()
	try:
		## build relay_map {ip : relayip}
		## build sub_map {relayip : [ip1, ip2, ...]}
		for line in lines_list:
			line = line.strip()
			if not line or line.startswith(cfg.POUND) or line.startswith(cfg.FLAG_TIPS) :
				continue
			else:
				ip, relay = line.split()
				relay_map[ip] = relay
				if relay in sub_map:
					sub_map[relay].append(ip)
				else:
					sub_map[relay] = [ip]
		## bulid iprelay_map { ip : [relay1, relay2, ...]}
		for ip in relay_map.keys():
			ip_list = [relay_map[ip]] # last node 
			ip_target = ip
			while relay_map[ip_target] in relay_map:
				relay = relay_map[ip_target]
				if relay_map[relay] == ip or relay_map[relay] in ip_list:
					## 出现回环
					print("[WARNING] relay_loop:[%s] with [%s]"%(ip, relay_map[relay]))
					print(ip_list)
					exit(1)
				ip_list.insert(0, relay_map[relay])
				ip_target = relay
			iprelay_map[ip] = ip_list
		## bulid ipsub_map {ip : ([subip1, subip2, ...])}
		for ip in list(sub_map.keys()):
			children_list = []
			getChildrenList(sub_map, ip, children_list)
			ipsub_map[ip] = set(children_list)
		if cfg.FLAG_DEBUG:
			print("iprelay_map:")
			print(iprelay_map)
			print("ipsub_map:")
			print(ipsub_map)
		return iprelay_map, ipsub_map
	except Exception as e:
		print((traceback.format_exc()))

def getChildrenList(sub_map, ip, children_list):
	"""
	迭代获取所有中继节点的后继节点
	Args:
		sub_map:当前的后继节点映射
		ip:当前IP
		children_list:当前IP的子节点
	"""
#	chilren_list = []
	if ip in sub_map:
		son_list = sub_map[ip]
		children_list += son_list
		#print("IP:" + ip + NEWLINE + ' '.join(children_list))
		for son in son_list:
			getChildrenList(sub_map, son, children_list)
