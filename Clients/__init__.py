from scapy.layers.inet import *
from queue import Queue

QueuePair = tuple[Queue[IP], Queue[IP]]