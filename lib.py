#!/usr/bin/env python3
# coding: utf-8


def get_filedata(filename):
    with open(filename, 'r') as f:
        data_list = [data.strip() for data in f.readlines()]
    return data_list
