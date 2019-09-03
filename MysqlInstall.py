#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Author :Yangky
# @TIME : 2019-09-02 17:43
import argparse, sys, paramiko, os, time

# from .my_cnf import init_mysql_cnf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from mysqlinstall import my_cnf


class MysqlInstall(object):
    def __init__(self, host, user, port, memory, *args, **kwargs):
        '''
        函数默认使用ssh(秘钥)方式来进行远程执行命令
        执行脚本机器环境：
            software_dir = /opt/mysql/
        此版本比较多人工判断，后期可根据固定特征来判断

        2期:
            添加 log模块+
            减少人员交互
            增加判断逻辑
        :param host:
        :param args:
        :param kwargs:
        '''
        self.host = host
        self.user = user
        self.port = port
        self.memory = memory
        self.software_dir = "/opt/mysql"
        self.base_dir = "/usr/local/mysql"
        self.mysql_packet = 'mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz'
        self.data_dir = '/data/mysql/mysql{}'.format(self.port)
        path = os.path.split(os.path.realpath(__file__))
        self.file_path = os.path.join(path[0])

    def remote_execute(self, cmd):
        # private_key = paramiko.RSAKey.from_private_key_file('/Users/yky/.ssh/id_rsa')   # 本机测试
        private_key = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.host, port=22, username=self.user, pkey=private_key)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read()
        ssh.close()
        return result

    def get_mysql_software_dir(self):
        '''
        函数是判断文件远程目录是否存在
        :return:
        '''
        input_result = ''
        soft_dir_result = self.remote_execute('ls -lh {}'.format(self.software_dir))
        if soft_dir_result:
            base_dir_result = self.remote_execute('ls -lh {}'.format(self.base_dir))
            if base_dir_result:
                print('当前软件版本及链接: \n{}'.format(base_dir_result.decode(encoding='utf8')))
                input_result = input(
                    "请检查base目录软连接、mysql版本是否正确:\n均正确请输入[ yes ]：\n版本问题，请输入[ mysql ]:\nbase目录软连接问题，请输入[ link ]:")
        return soft_dir_result, input_result

    def init_mysql_soft_dir(self):
        '''
        没有 /opt/mysql情况下，就拷贝特定版本的mysql到远端
        "scp -rf {0}/mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz {1}@{2}:{0}/".format(self.software_dir,self.user,self.host)
        "tar -zxvf {0}/mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz -C {0}".format(self.software_dir)
        :return:
        '''
        scp_mysql_packet_cmd = "scp  {0}/mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz {1}@{2}:{0}/".format(
            self.software_dir, self.user, self.host)
        tar_mysql_packet_cmd = "tar -zxvf {0}/mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz -C {0}".format(
            self.software_dir)
        link_mysql_packet_cmd = "ln -s {0}/mysql-5.7.24-linux-glibc2.12-x86_64 {1}".format(self.software_dir,
                                                                                           self.base_dir)
        if not self.remote_execute('ls {0}/mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz '.format(self.software_dir)):
            os.system(scp_mysql_packet_cmd)

        tar_packet_result = self.remote_execute(tar_mysql_packet_cmd)
        link_mysql_base_result = self.remote_execute(link_mysql_packet_cmd)

        self.remote_execute('groupadd mysql && useradd -g mysql -s /sbin/nologin -d /usr/local/mysql -MN mysql')
        self.remote_execute('chown -R mysql.mysql {}'.format(self.data_dir))

        if tar_packet_result:
            return "mysql packet init complete!"
        elif link_mysql_base_result:
            return "mysql packet init fail "
        else:
            return

    def relink_mysql_dir(self):
        pass

    def init_mysql(self):
        self.remote_execute('mkdir -p %s/{data,logs,tmp}' % (self.data_dir))

        default_file = 'my{}.cnf'.format(self.port)
        host_last = self.host.split('.')[3]
        server_id_new = '{}{}'.format(host_last, self.port)

        my_cnf_str = my_cnf.init_mysql_cnf(self.base_dir, self.data_dir, self.memory, self.port, server_id_new)
        with open(default_file, 'w', encoding='utf8') as f:
            f.write(my_cnf_str)

        check_mycnf_exists = self.remote_execute(
            'ls {0}/{1} '.format(self.data_dir, default_file))
        if check_mycnf_exists:
            print("请检查配置文件是否存在:", check_mycnf_exists.decode(encoding='utf8'), )
            return None
        else:
            os.system('scp {0} {1}@{2}:{3}'.format(default_file, self.user, self.host, self.data_dir))  # 拷贝配置文件到指定dir

        self.remote_execute('groupadd mysql && useradd -g mysql -s /sbin/nologin -d /usr/local/mysql -MN mysql')
        self.remote_execute('chown -R mysql.mysql {}'.format(self.data_dir))
        init_mysql_cmd = "{0}/bin/mysqld --defaults-file={1}/{2} --initialize ".format(self.base_dir, self.data_dir,
                                                                                       default_file)
        init_result = self.remote_execute(init_mysql_cmd)
        # if init_result:
        #     return '初始化失败，请检查环境。'

        time.sleep(30)
        self.remote_execute(
            "{0}/bin/mysqld --defaults-file={1}/{2} & ".format(self.base_dir, self.data_dir, default_file))
        time.sleep(5)
        tmp_passwd = self.remote_execute(
            "cat %s|grep temporary|awk -F 'localhost: ' '{print $2}'" % (self.data_dir + '/logs/error.log'))
        tmp_passwd = tmp_passwd.decode(encoding='utf8').rstrip("\n")
        change_passwd_cmd = " alter user user() identified by \'111111\' "
        mysql_change_password = '/usr/local/mysql/bin/mysql -uroot -p \'{0}\' -S {1} -e \'{2}\''.format(tmp_passwd,
                                                                                                        self.data_dir + 'tmp/mysql.sock',
                                                                                                        change_passwd_cmd)
        print(mysql_change_password)
        self.remote_execute(mysql_change_password)

        self.remote_execute('echo "export PATH=$PATH:/usr/local/mysql/bin" >> /etc/profile && source /etc/profile')

    def start_mysql(self):
        pass


def run(host, user, port, memory):
    mysql_instance = MysqlInstall(host, user, port, memory)
    soft_dir_result, base_dir_result = mysql_instance.get_mysql_software_dir()
    mysql_instance.remote_execute('mkdir -p {}'.format(mysql_instance.software_dir))
    if base_dir_result == 'yes':
        print('检查目录正确，不需要重写解压目录')
        mysql_instance.init_mysql()

    elif base_dir_result == "mysql":
        print('mysql 版本问题，下载mysql，传输到远程host')
        ret = mysql_instance.init_mysql_soft_dir()
        print(ret)

    elif base_dir_result == "link":
        print("软连接有问题，请联系管理员")
    else:
        print('其他问题，请联系管理员')


if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="[初始化mysql]")
    parse.add_argument('-H', '--ip', type=str, help='请输入初始化主机host')
    parse.add_argument('-P', '--port', type=int, help='请输入初始化mysql端口')
    parse.add_argument('-U', '--user', type=str, help='请输入远程用户名')
    # parse.add_argument('-p', '--password', type=str, help='请输入远程密码')
    parse.add_argument('-M', '--memory', type=str, help='请输入初始化mysql I_B_P内存默认单位M/G')
    ip, port, memory, user = parse.parse_args().ip, parse.parse_args().port, parse.parse_args().memory, parse.parse_args().user

    if not ip:
        print("Some Err,input '-h' for help.")
        sys.exit()
    else:
        run(ip, user, port, memory)
