# mt
Tunnel IPv4 traffic using ICMP or UDP as transfer protocols.
Uses TUN/TAP interfaces which only works on linux.

## Prerequisites
- python 3.11
- python-venv

## Setup

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
. .venv/bin/activate
python . -h
```

## Updating requirements.txt
```sh
pip freeze > requirements.txt
```

<details>
<summary>Old setup</summary>

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
```

### Cleanup

```sh
ip link del dev mt
```

</details>