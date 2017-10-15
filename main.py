# coding: utf-8

from pexpect import pxssh


def connect(host, user, password):
    try:
        s = pxssh.pxssh()
        s.login(host, user, password)
        return s
    except:
        print('[-] Error Connecting')
        exit(0)


def send_command(s, cmd):
    s.sendline(cmd)
    s.prompt()
    print(s.before)


def main():
    s = connect('127.0.0.1', 'root', 'root')
    send_command(s, 'cat /etc/shadow | grep root')


if __name__ == '__main__':
    main()
