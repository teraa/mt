#!/bin/bash
# run as root
set -e

ip tuntap add dev mt mode tun user tera
ip address add dev mt 10.20.0.1/24
ip link set dev mt up
# ip link set dev mt mtu 1212
# ip link del dev mt
# sudo setcap CAP_NET_RAW,CAP_NET_ADMIN=eip $(readlink -f $(which python3.11))
