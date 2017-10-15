# coding: utf-8

import nmap


def append_ip(ip, filename='./ip_list.txt'):
    with open(filename, 'a') as f:
        f.write('%s\n' % ip)


def scan_ssh(ip_block, port=22):
    nm = nmap.PortScannerYield()
    for ip, host in nm.scan('%s.1/24' % ip_block, str(port)):
        try:
            state = host['scan'][ip]['tcp'][port]['state']
            print('ip: %s  state: %s' % (ip, host['scan'][ip]['tcp'][port]['state']))
            if state == 'open':
                append_ip(ip)
        except:
            print('ip: %s  state: error' % ip)


def main():
    for i in range(0, 256):
        scan_ssh('47.52.%s' % i)


if __name__ == '__main__':
    main()
