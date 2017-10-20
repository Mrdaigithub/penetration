#!/usr/bin/env python3
# coding: utf-8

from Asyncpwd import Asyncpwd
import multiprocessing, lib


class Processhost:
    def __init__(self, hfile, pfile, processlen=multiprocessing.cpu_count()):
        hosts = lib.get_filedata(hfile)
        process = multiprocessing.Pool(processlen)
        for host in hosts:
            process.apply_async(Asyncpwd, args=(pfile, host,))
        process.close()
        process.join()
