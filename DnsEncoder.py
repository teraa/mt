import base64
from math import ceil

SEGMENT_SIZE = 63
TOTAL_SIZE = 254

def pad_base32(input: str) -> str:
    return input + '=' * (-len(input) % 8)

class DnsEncoder(object):
    def __init__(self, domain: str) -> None:
        domain = domain.rstrip('.') + '.'
        self.domain = domain

        total_size = TOTAL_SIZE - len(domain)
        total_size = total_size - ceil(total_size / SEGMENT_SIZE)
        self.total_size = total_size

    def encode(self, data: bytes) -> list[str]:
        b32 = base64.b32encode(data).rstrip(b'=')

        result = []

        for i in range(0, len(b32), self.total_size):
            name = ''

            for j in range(i, min(i + self.total_size, len(b32)), SEGMENT_SIZE):
                k = min(j + SEGMENT_SIZE, i + self.total_size, len(b32))
                name = f'{name}{b32[j:k].decode()}.'

            name = f'{name}{self.domain}'

            result.append(name)
        return result

    def decode(self, names: list[str]) -> bytes:
        b32 = ''.join([n.rstrip(self.domain).replace('.', '') for n in names])
        b32 = pad_base32(b32)
        data = base64.b32decode(b32)
        return data

# encoder = DnsEncoder('example.org')
# input = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ.0123456789\n'*10+']'
# names = encoder.encode(str.encode(input))
# for name in names: print(name)
# data = encoder.decode(names)
# print(data.decode())
