# epics-stress-test

Tools for stress-testing EPICS IOC using multiple emulated clients.

## Requirements

+ The device with the IOC being tested. We used this [IOC template](https://github.com/binp-automation/devsup-template/tree/5b3ea3d50d07d39632bc940cab982194c1aca67e).
+ Host device with relatively high performance to run these tools.
+ TCP/IP link between between these two devices with addresses like `10.1.0.x/16`.

## Usage

+ Create multiple `macvlan` interfaces on host:
```bash
sudo python3 ./macvlan.py <iface> <number-of-clients>
```
+ Export EPICS environmental variables both on host and device being tested:
```bash
export EPICS_BASE=</path/to/epics-base>
export EPICS_HOST_ARCH=$($EPICS_BASE/startup/EpicsHostArch)
export PATH=$PATH:$EPICS_BASE/bin/$EPICS_HOST_ARCH/
export EPICS_CA_AUTO_ADDR_LIST=NO
export EPICS_CA_ADDR_LIST=10.1.255.255
```
+ Run IOC on device. IOC should have `WAVEFORM` pv.

+ On host create and connect emulated clients:
```bash
python3 ./camonitor.py <number-of-clients>
```

+ On host update waveform and see client messages:
```bash
python3 ./caput.py <number-of-updates> > /dev/null
```
