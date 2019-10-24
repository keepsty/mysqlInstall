#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Author :Yangky
# @TIME : 2019-09-03 09:55

import argparse, sys, paramiko, os, time
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from mysqlinstall import MysqlInstall

mysql_cmd = '''/usr/local/mysql/bin/mysql -uroot -p "{0}" -S {1} -e " select user,host from mysql.user where host = 'localhost' " '''.format(
    '06c=.ik5a/Kg', "/data/mysql/mysql3308/tmp/mysql.sock", )

ret = MysqlInstall.run('172.16.111.131', 'root', '3308', '128M')
