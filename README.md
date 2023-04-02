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