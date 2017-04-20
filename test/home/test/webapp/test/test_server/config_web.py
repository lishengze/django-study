#coding=utf-8

CONSOLE_PATH = "/home/test/console/"
CONSOLE_WORK_PATH = CONSOLE_PATH + "scripts/"

PROJECT_NAME = "mysite"
APP_NAME = "blog"


TEMPLATES_PATH = "/home/test/webapp/" + PROJECT_NAME + "/templates"

IP_ADDR = '172.1.128.170'

ENV_DICT_KEY = ['TEST_170', 'PTEST_170', 'MYTEST_170']

ENV_DICT = {
	'TEST_170':['MONITOR2 开发测试环境', '172.1.128.170', 18888],
	'PTEST_170':['MONITOR2 生产测试环境', '172.1.128.170', 19999],
	'MYTEST_170':['MONITOR2 开发环境', '172.1.128.170', 20000]
	}
