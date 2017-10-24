#!/usr/bin/env python3
# coding: utf-8


def foreachcsv(filename, callback):
    with open(filename, 'rb') as f:
        while True:
            line = f.readline().strip()
            if not line:
                break
            callback(line)
