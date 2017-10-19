# coding: utf-8

import asyncio, asyncssh, math
import multiprocessing

ASYNC_LEN = 5


def get_data_form_file(filename):
    with open(filename, 'r') as f:
        data_list = [data.strip() for data in f.readlines()]
    return data_list


async def run_client(host, password):
    print('host: %s  start test' % host, password)
    async with asyncssh.connect(host=host, port=22, username='root', password=password, known_hosts=None) as conn:
        return await conn.run("echo '%s'" % password), 1


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
            print('Task %d succeeded:' % i, result.stdout)
            with open('log.txt', 'a') as fg:
                fg.write(host + ':' + result.stdout)


def process_task(host, passwords):
    count = math.ceil(len(passwords) / ASYNC_LEN)
    loop = asyncio.get_event_loop()
    for i in range(int(count)):
        loop.run_until_complete(run_multiple_clients(host, passwords[i * ASYNC_LEN: i * ASYNC_LEN + ASYNC_LEN]))
    loop.close()


if __name__ == '__main__':
    passwords = get_data_form_file('pwd.txt')
    hosts = get_data_form_file('ip.txt')
    process = multiprocessing.Pool(multiprocessing.cpu_count())
    for host in hosts:
        process.apply_async(process_task, args=(host, passwords))
    process.close()
    process.join()
