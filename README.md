# mt

## Description

Tunnel IPv4 traffic using ICMP or UDP as transfer protocols.
Uses TUN/TAP interfaces which only works on linux.

## Prerequisites

- python 3.11
- python-venv

## Initial setup

```sh
# init venv
python -m venv .venv
. .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# set capabilities
sudo setcap CAP_NET_RAW,CAP_NET_ADMIN=eip $(readlink -f $(which python3.11))
```

## Run

```sh
. .venv/bin/activate # once per session
python . -h
```

```
Options:
  -h, --help       show this help message and exit
  --tif=TIF        name of the TUN interface to use [mt]
  --taddr=TADDR    TUN address [10.20.0.1]
  --tmask=TMASK    TUN netmask [255.255.255.0]
  --tmtu=TMTU      TUN MTU [1472]
  --lif=LIF        name of the interface to listen on [enp0s8]
  --laddr=LADDR    listen address [0.0.0.0]
  --lport=LPORT    listen port [50142]
  --raddr=RADDR    remote address [192.168.56.106]
  --rport=RPORT    remote port [50142]
  --mode=MODE      mode (protocol): udpc, udps, dnsc, dnss or icmp [udps]
  --domain=DOMAIN  domain to use for DNS tunneling [example.org]
```

### Examples
```sh
# ICMP client A
python . --taddr 10.20.0.1 --mode icmp --lif enp0s8 --raddr 192.168.56.106
# ICMP client B
python . --taddr 10.20.0.2 --mode icmp --lif enp0s8 --raddr 192.168.56.105

# UDP client
python . --taddr 10.20.0.1 --mode udpc --raddr 192.168.56.106
# UDP server
python . --taddr 10.20.0.2 --mode udps

# DNS client
python . --taddr 10.20.0.1 --mode dnsc --raddr 192.168.56.106
# DNS server
python . --taddr 10.20.0.2 --mode dnss
```

---

## Forwarding traffic out to the Internet (optional)

### Client side configuration

```sh
ip route add 0.0.0.0/1 dev mt
ip route add 128.0.0.0/1 dev mt
ip route add ${server_ip}/32 via ${gateway} dev ${interface}
```

- [reference](https://www.wireguard.com/netns/#the-classic-solutions)

#### Find gateway and interface

```sh
ip r l default
```

e.g.

> default via 10.0.2.2 dev enp0s3 proto dhcp src 10.0.2.15 metric 100

- gateway: `10.0.2.2` 
- interface: `enp0s3`

### Server side configuration

#### Allow forwarding connections out to internet

```sh
iptables -A FORWARD -i mt -j ACCEPT
```

#### Enable IP forwarding

1. Create `/etc/sysctl.d/local.conf`
    ```properties
    net.ipv4.ip_forward=1
    ```
2. Reboot or `sysctl --system`

---

### Misc/info

#### Updating requirements.txt

```sh
pip freeze > requirements.txt
```

#### Disabling multicast

To reduce noise on the TUN interface, you can disable multicast
```sh
ip link set dev mt multicast off
```

---

<details>
<summary>Old setup (ignore)</summary>

## Manual TUN Setup (info)

### Setup

```sh
#!/bin/bash
# run as root
set -e

ip tuntap add dev mt mode tun user tera
ip address add dev mt 10.20.0.1/24
ip link set dev mt up
ip link set dev mt mtu 1500
ip link set dev mt multicast off
```

### Cleanup

```sh
ip link del dev mt
```

</details>