import sys
import os
from subprocess import run, PIPE
from time import sleep

import macvlan


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) >= 2 else 1

    ret = run("caget -t WAVEFORM.NELM".split(" "), stdout=PIPE)
    assert ret.returncode == 0
    nelm = int(ret.stdout)

    for k in range(n):
        data = [str(i + nelm*k) for i in range(nelm)];
        ret = run(("caput -at WAVEFORM %d %s" % (nelm, " ".join(data))).split(" "))
        assert ret.returncode == 0
