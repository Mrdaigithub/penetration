#!/usr/bin/env python3
# coding: utf-8

import multiprocessing
import asyncssh
import asyncio
import math
from units import units


class Conn:
    def __init__(self, host='127.0.0.1',
                 username='root',
                 password='root',
                 port=22,
                 known_hosts=None,
                 process_num=multiprocessing.cpu_count(),
                 thread_num=5,
                 timeout=5):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.known_hosts = known_hosts
        self.process_num = process_num
        self.thread_num = thread_num
        self.timeout = timeout
        self.error_count = 0
        self.found = False

    async def run_client(self, host=None, password=None):
        if not host:
            host = self.host
        if not password:
            password = self.password
        async with asyncssh.connect(host=host,
                                    username=self.username,
                                    password=password,
                                    port=self.port,
                                    known_hosts=self.known_hosts) as conn:
            return await conn.run('echo "Found password: %s"' % self.password)

    async def run_multiple_hosts(self, hosts, callback):
        tasks = (asyncio.wait_for(self.run_client(host=host), timeout=self.timeout) for host in hosts)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                if str(result) == '':
                    print('Task %s failed: Time out' % hosts[i - 1])
                elif str(result) == 'Disconnect Error: Permission denied':
                    callback(hosts[i - 1])
                else:
                    print('Task %s failed: %s' % (hosts[i - 1], result))
            elif result.exit_status != 0:
                print('Task %s exited with status %s:' % (hosts[i - 1], result.exit_status))
                print(result.stderr, end='')
            else:
                print('Task %s succeeded: ' % hosts[i - 1])

    async def run_multiple_password(self, passwords, trash_callback, find_callback):
        tasks = (asyncio.wait_for(self.run_client(password=password), timeout=self.timeout) for password in passwords)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                if str(result) != 'Disconnect Error: Permission denied':
                    self.error_count += 1
                print('Host: %s Password: %s failed: %s' % (self.host, passwords[i - 1], result))
            elif result.exit_status != 0:
                print(
                    'Host: %s Password: %s exited with status %s:' % (self.host, passwords[i - 1], result.exit_status))
                print(result.stderr, end='')
                self.error_count += 1
            else:
                print('Host: %s Password: %s succeeded: ' % (self.host, passwords[i - 1]), end='')
                find_callback(self.host, passwords[i - 1])
                self.found = True

    def test_hosts(self, loop_instance, hosts_filename, callback):
        hosts = []
        with open(hosts_filename, 'r') as f:
            while True:
                line = f.readline().strip()
                if not line:
                    if len(hosts):
                        loop_instance.run_until_complete(self.run_multiple_hosts(hosts, callback))
                    break
                if len(hosts) > self.thread_num:
                    loop_instance.run_until_complete(self.run_multiple_hosts(hosts, callback))
                    hosts = []
                hosts.append(line)

    def test_passwords(self, passwords_filename, trash_callback, find_callback):
        passwords = units.fdata2list(passwords_filename)
        max_error = math.ceil(len(passwords) * 0.05)
        password_count = math.ceil(len(passwords) / self.thread_num)
        loop = asyncio.get_event_loop()
        while password_count:
            if self.error_count > max_error:
                trash_callback(self.host)
                return False
            if self.found:
                return True
            loop.run_until_complete(
                self.run_multiple_password(passwords[:self.thread_num], trash_callback, find_callback))
            passwords = passwords[self.thread_num:]
            password_count = math.ceil(len(passwords) / self.thread_num)
        trash_callback(self.host)
