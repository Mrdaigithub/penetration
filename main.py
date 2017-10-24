#!/usr/bin/env python3
# coding: utf-8

from units import units
from sshconnector import sshconnector
import redis
import asyncio

r = redis.Redis(host='127.0.0.1', port=6379, db=0)


def save_host(host):
    r.sadd('host:unuse', host)
    r.save()


if __name__ == '__main__':
    conn = sshconnector.Conn(thread_num=20)
    loop = asyncio.get_event_loop()
    conn.test_hosts(loop, './data/ip.csv', save_host)
