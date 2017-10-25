#!/usr/bin/env python3
# coding: utf-8

from gui import gui
import core

if __name__ == '__main__':
    app = gui.Application(add_unuse_hosts=core.add_unuse_hosts, try_passwords=core.try_password)
    app.master.title('Penetration')
    app.mainloop()
