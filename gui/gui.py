#!/usr/bin/env python3
# coding: utf-8

import tkinter.messagebox as messagebox
from tkinter import *


class Application(Frame):
    def __init__(self, master=None, add_unuse_hosts=None, try_passwords=None):
        Frame.__init__(self, master)
        self.add_unuse_hosts = add_unuse_hosts
        self.try_passwords = try_passwords
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.add_unuse_hosts_button = Button(self, text='add unuse hosts', command=self.add_unuse_hosts)
        self.add_unuse_hosts_button.pack()
        self.try_passwords_button = Button(self, text='try passwords', command=self.try_passwords)
        self.try_passwords_button.pack()
