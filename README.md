# mysqlInstall

1. 工具使用python3编写并执行
2. git 名字为mysqlInstall 如果clone下来使用会报错
   ModuleNotFoundError: No module named 'mysqlinstall'
   解决办法：
    mv mysqlInstall mysqlinstall
  后期会改
3. 脚本目录结构：

[root@mysql1 mysqlinstall]# ll
total 40
-rw-r--r--. 1 root root   91 Sep  3 04:43 __init__.py

-rw-r--r--. 1 root root 4499 Sep  3 05:18 my3308.cnf    -- 生成的配置文件，scp方式拷贝到远端

-rw-r--r--. 1 root root 5062 Sep  3 04:43 my_cnf.py     -- 配置文件模板

-rw-r--r--. 1 root root 8245 Sep  3 05:17 MysqlInstall.py

-rw-r--r--. 1 root root  354 Sep  3 04:43 mysql_user_init

drwxr-xr-x. 2 root root  101 Sep  3 04:45 __pycache__

-rw-r--r--. 1 root root  541 Sep  3 04:45 test.py

4. 软件包存放（同远端）目录：
[root@mysql1 mysqlinstall]# cd /opt/mysql
[root@mysql1 mysql]# pwd
/opt/mysql
[root@mysql1 mysql]# ll


-rw-r--r--. 1 root root 644930593 Sep  2 23:13 mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz

5. 执行命令案例：
  命令提示：
    python3 MysqlInstall.py -h
    
  python3 MysqlInstall.py -H 172.16.111.131 -P 3308 -M 128M -U root

6. 其他问题，欢迎留言。
