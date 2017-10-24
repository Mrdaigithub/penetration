#!/usr/bin/env python3
# coding: utf-8

from units import units
from sshconnector import sshconnector
import redis

r = redis.Redis(host='127.0.0.1', port=6379, db=0)


def save_host(host):
    r.sadd('host:unuse', host)
    r.save()


if __name__ == '__main__':
    conn = sshconnector.Conn(thread_num=10)
    conn.test_hosts('./data/ip.csv', save_host)
