import sys
import os
from time import time, sleep
from subprocess import run, Popen, PIPE, STDOUT
from threading import Thread, Lock

import macvlan


class Accounter:
    def __init__(self, n):
        self.mutex = Lock()
        self.ptrs = {}
        self.replies = {}
        self.n = n

        self.timeout = 4.0
        self.quit = False
        self.thread = Thread(target=self._thread_loop)
        self.thread.start()

    def _thread_loop(self):
        while not self.quit:
            self.check()
            sleep(1.0)

    def _get_reply(self, i):
        j = self.ptrs.get(i, 0)
        reply = self.replies.get(j, {
            "count": 0,
            "update": time(),
            "data": {},
        })
        self.replies[j] = reply
        self.ptrs[i] = j + 1
        return reply

    @staticmethod
    def _print_reply(reply):
        print()
        for k, v in reply["data"].items():
            print("%d: %s" % (v, k))

    def check(self):
        with self.mutex:
            for (idx, reply) in self.replies.items():
                if reply["count"] < n and time() - reply["update"] > self.timeout:
                    count = reply["data"].get(None, 0)
                    dn = (n - reply["count"])
                    reply["data"][None] = count + dn
                    reply["count"] = n
                    reply["update"] = time()

                    print("+"*dn, end="")
                    sys.stdout.flush()
                    self._print_reply(reply)

                    for j in self.ptrs.values():
                        if j <= idx:
                            self.ptrs[j] = idx + 1

    def report(self, i, data):
        trn = 64
        data = (data[:trn] + b'..') if len(data) > trn else data
        with self.mutex:
            reply = self._get_reply(i);
            
            reply["count"] += 1
            count = reply["data"].get(data, 0)
            count += 1;
            reply["data"][data] = count
            reply["update"] = time()
            
            print("+", end="")
            sys.stdout.flush()
            if reply["count"] >= n:
                self._print_reply(reply)


def monitor(i, proc, acc):
    for l in proc.stdout:
        acc.report(i, l)

if __name__ == "__main__":
    n = int(sys.argv[1])
    acc = Accounter(n)

    ret = run("gcc -nostartfiles -fpic -shared bind.c -o bind.so -ldl -D_GNU_SOURCE".split(" "))
    assert ret.returncode == 0

    ps = []
    try:
        for i in range(1, n + 1):
            env = os.environ.copy();
            #env["EPICS_CAS_INTF_ADDR_LIST"] = macvlan.ip(i)
            env["BIND_ADDR"] = macvlan.ip(i)
            env["LD_PRELOAD"] = "./bind.so"
            p = Popen("camonitor WAVEFORM".split(" "), env=env, stdout=PIPE, stderr=STDOUT)
            t = Thread(target=lambda: monitor(i, p, acc))
            t.start()
            ps.append((i, p, t))

        while True:
            sleep(1)
    except KeyboardInterrupt:
        try:
            for (i, p, t) in ps:
                p.terminate()
                t.join()
            acc.quit = True
            acc.thread.join()
        except:
            pass
