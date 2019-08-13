import sys
from subprocess import run


def run_cmd(cmd):
    print(cmd)
    ret = run(cmd.split(" "))
    assert ret.returncode == 0

def mac(n):
    a = "00:11"
    for i in range(4):
        a += ":%02x" % ((n >> ((3-i)*8)) & 0xff)
    return a

def ip(n):
    return "10.1.%d.%d" % (n//255 + 1, n % 255)

def setup_macvlan(iface, n):
    run_cmd("ip link add link %s address %s %s.%s type macvlan" % (iface, mac(n), iface, n))

def set_ip(iface, n):
    run_cmd("ip addr add %s/16 dev %s.%s" % (ip(n), iface, n))

def set_up(iface, n):
    run_cmd("ip link set %s.%s up" % (iface, n))

def add_route(iface, n):
    run_cmd("sudo ip route add 10.1.0.0/16 via %s dev %s.%s" % (ip(n), iface, n))

def del_route(iface, n):
    run_cmd("sudo ip route del 10.1.0.0/16 dev %s.%s" % (iface, n))

def setup_link(iface, n):
    setup_macvlan(iface, n)
    set_ip(iface, n)
    set_up(iface, n)

def delete_link(iface, n):
    run_cmd("ip link del %s.%s" % (iface, n))

def cleanup(iface):
    try:
        for i in range(1, 2**16):
            delete_link(iface, i)
    except:
        pass

if __name__ == "__main__":
    iface = sys.argv[1]
    if sys.argv[2] == "cleanup":
        cleanup(iface)
    else:
        n = int(sys.argv[2])
        for i in range(1, n + 1):
            setup_link(iface, i)
