import ipaddress
import subprocess

iplist = [ipaddress.ip_address('192.168.1.100'), ipaddress.ip_address('192.168.1.101'), 'yandex.ru']


def host_ping(hosts):
    res = dict()
    for addr in hosts:
        args = ['ping', str(addr)]
        subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
        m_list = []
        for line in subproc_ping.stdout:
            line = line.decode('cp866').encode('utf-8').decode('utf-8')
            m_list.append(line)
        if 'TTL' in m_list[3]:
            res[str(addr)] = 'Доступен'
        else:
            res[str(addr)] = 'Недоступен'
    return res


print(host_ping(iplist))
