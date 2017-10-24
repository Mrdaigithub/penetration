#!/usr/bin/env python3
# coding: utf-8

import asyncssh
import asyncio
import multiprocessing


class Conn:
    def __init__(self, host='127.0.0.1',
                 username='root',
                 password='root',
                 port=22,
                 known_hosts=None,
                 process_num=multiprocessing.cpu_count(),
                 thread_num=5):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.known_hosts = known_hosts
        self.process_num = process_num
        self.thread_num = thread_num
        self.loop = asyncio.get_event_loop()

    async def run_client(self, host=None, password=None):
        print('run shh%s@%s' % (self.username, host))
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
        tasks = (asyncio.wait_for(self.run_client(host=host), timeout=5) for host in hosts)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                if str(result) == 'Disconnect Error: Permission denied':
                    callback(hosts[i - 1])
                print('Task %d failed: %s' % (i, result))
            elif result.exit_status != 0:
                print('Task %d exited with status %s:' % (i, result.exit_status))
                print(result.stderr, end='')
            else:
                print('Task %d succeeded: ' % i, end='')
                print(result.stdout, end='')

    async def run_multiple_password(self, passwords):
        tasks = (self.run_client(password) for password in passwords)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print('Task %d failed: %s' % (i, result))
            elif result.exit_status != 0:
                print('Task %d exited with status %s:' % (i, result.exit_status))
                print(result.stderr, end='')
            else:
                print('Task %d succeeded: ' % i, end='')
                print(result.stdout, end='')

    def test_hosts(self, hosts_filename, callback):
        hosts = []
        with open(hosts_filename, 'r') as f:
            while True:
                line = f.readline().strip()
                if not line:
                    if len(hosts):
                        self.loop.run_until_complete(self.run_multiple_hosts(hosts, callback))
                    break
                if len(hosts) > self.thread_num:
                    print(hosts)
                    self.loop.run_until_complete(self.run_multiple_hosts(hosts, callback))
                    hosts = []
                hosts.append(line)

    def test_passwords(self, passwords):
        if not isinstance(passwords, list):
            print('argument passwords is not a list')
            return False
        password_count = math.ceil(len(passwords) / self.thread_num)
        loop = asyncio.get_event_loop()
        while password_count:
            loop.run_until_complete(self.run_multiple_hosts(passwords[:self.thread_num]))
            passwords = passwords[self.thread_num:]
            password_count = math.ceil(len(passwords) / self.thread_num)
