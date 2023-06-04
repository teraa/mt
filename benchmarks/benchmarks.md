PC1

```sh
# direct
iperf3 -c 192.168.56.106 -J > direct-tcp.json
iperf3 -c 192.168.56.106 -J -u > direct-udp.json

# UDP
mt --taddr 10.20.0.1 udpc --addr 192.168.56.106
iperf3 -c 10.20.0.2 -J > udpc-tcp.json
iperf3 -c 10.20.0.2 -J -u > udpc-udp.json

# DNS
mt --taddr 10.20.0.1 dnsc --addr 192.168.56.106
iperf3 -c 10.20.0.2 -J > dnsc-tcp.json
iperf3 -c 10.20.0.2 -J -u > dnsc-udp.json

# ICMP
mt --taddr 10.20.0.1 icmp --lif enp0s8 --raddr 192.168.56.106
iperf3 -c 10.20.0.2 -J > icmpc-tcp.json
iperf3 -c 10.20.0.2 -J -u > icmpc-udp.json
```


PC2

```sh
iperf3 -s

# UDP
mt --taddr 10.20.0.2 udps

# DNS
mt --taddr 10.20.0.2 dnss

# ICMP
mt --taddr 10.20.0.2 icmp --lif enp0s8 --addr 192.168.56.105
```

Show results
```sh
jq '.end | [.sum_sent, .sum_received] | [.[].bits_per_second] | {send: .[0], recv: .[1]}' results.json
```
