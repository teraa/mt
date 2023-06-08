#!/usr/bin/env bash
set -e

test -d .venv || pushd ..
. .venv/bin/activate

lif=enp0s8
taddr=10.20.0.1
traddr=10.20.0.2
raddr=192.168.56.106
delay=5
duration=60

mt_opts=(
    "--taddr $taddr udpc --addr $raddr"
    "--taddr $taddr dnsc --addr $raddr"
    "--taddr $taddr icmp --lif $lif --addr $raddr"
)

for mt_opt in "${mt_opts[@]}"; do

    mode=$(cut -d' ' -f3 <<< ${mt_opt})

    python -m mt ${mt_opt} > mt.log 2>&1 &
    pid=$!
    trap "kill $pid; exit" SIGINT

    for traffic in {tcp,udp}; do

        for direction in {normal,reverse}; do
            
            iperf_opt="-c $traddr -t $duration"
            file="benchmarks/results/$mode-$traffic"

            if [[ "$traffic" == "udp" ]]; then
                iperf_opt="$iperf_opt -ub0"
            fi

            if [[ "$direction" == "reverse" ]]; then
                iperf_opt="$iperf_opt -R"
                file="$file-r"
            fi

            file="$file.json"

            echo "Writing to $file"
            iperf3 $iperf_opt -J | jq > $file

            echo "Waiting $delay seconds to clear buffers..."
            sleep $delay

        done
    done
    read -p $'Advance server tunnel mode and press enter to continue\n'
    
    echo "killing mt"
    kill $pid || true

done
