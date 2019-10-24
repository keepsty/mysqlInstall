#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Author :Yangky
# @TIME : 2019-09-10 18:43

import pymysql

int_time = "show global variables like 'interactive_timeout'"
wait_time = "show global variables like 'wait_timeout'"
change_int_time = "set global interactive_timeout=15"

conn = pymysql.Connect(host='172.16.111.131', user='yang', password='111111', port=3308)
cur = conn.cursor()

# 查看初始值
cur.execute(int_time)
int_ret = cur.fetchone()
cur.execute(wait_time)
wait_ret = cur.fetchone()

cur.close()

cur = conn.cursor()
print('before', int_ret, wait_ret)

# 查看初始值
cur.execute(change_int_time)
cur.execute(int_time)
int_ret = cur.fetchone()
cur.execute(wait_time)
wait_ret = cur.fetchone()
cur.close()
print('after', int_ret, wait_ret)
