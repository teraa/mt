# Benchmarks

## PC1

```sh
# direct
iperf3 -c 192.168.56.106 -t 60 -J > direct-tcp.json
iperf3 -c 192.168.56.106 -t 60 -Jub0 > direct-udp.json
ping 192.168.56.106 -A -w10 > direct.txt

# UDP
mt --taddr 10.20.0.1 udpc --addr 192.168.56.106
iperf3 -c 10.20.0.2 -t 60 -J > udpc-tcp.json
iperf3 -c 10.20.0.2 -t 60 -J -R > udpc-tcp-r.json
iperf3 -c 10.20.0.2 -t 60 -Jub0 > udpc-udp.json
iperf3 -c 10.20.0.2 -t 60 -Jub0 -R > udpc-udp-r.json
ping 10.20.0.2 -A -w10 > udp.txt

# DNS
mt --taddr 10.20.0.1 dnsc --addr 192.168.56.106
iperf3 -c 10.20.0.2 -t 60 -J > dnsc-tcp.json
iperf3 -c 10.20.0.2 -t 60 -J -R > dnsc-tcp-r.json
iperf3 -c 10.20.0.2 -t 60 -Jub0 > dnsc-udp.json
iperf3 -c 10.20.0.2 -t 60 -Jub0 -R > dnsc-udp-r.json
ping 10.20.0.2 -A -w10 > dns.txt

# ICMP
mt --taddr 10.20.0.1 icmp --lif enp0s8 --addr 192.168.56.106
iperf3 -c 10.20.0.2 -t 60 -J > icmp-tcp.json
iperf3 -c 10.20.0.2 -t 60 -J -R > icmp-tcp-r.json
iperf3 -c 10.20.0.2 -t 60 -Jub0 > icmp-udp.json
iperf3 -c 10.20.0.2 -t 60 -Jub0 -R > icmp-udp-r.json
ping 10.20.0.2 -A -w10 > icmp.txt
```

## PC2

```sh
iperf3 -s

# UDP
mt --taddr 10.20.0.2 udps

# DNS
mt --taddr 10.20.0.2 dnss

# ICMP
mt --taddr 10.20.0.2 icmp --lif enp0s8 --addr 192.168.56.105
```

## List results

```sh
jq '.end | [.sum_sent, .sum_received] | [.[].bits_per_second] | {send: .[0], recv: .[1]}' results.json
```
