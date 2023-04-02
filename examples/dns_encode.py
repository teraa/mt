import base64
from math import ceil

SEGMENT_SIZE = 63
TOTAL_SIZE = 254
DOMAIN = 'example.org.'
TOTAL_SIZE = TOTAL_SIZE - len(DOMAIN)
TOTAL_SIZE = TOTAL_SIZE - ceil(TOTAL_SIZE / SEGMENT_SIZE)

# 012345678901234567890123456789012345678901234567890123456789012.012345678901234567890123456789012345678901234567890123456789012.012345678901234567890123456789012345678901234567890123456789012.0123456789012345678901234567890123456789012345678.example.org.


def encode(data: bytes) -> list[str]:
    b32 = base64.b32encode(data).rstrip(b'=')

    result = []

    for i in range(0, len(b32), TOTAL_SIZE):
        name = ''

        for j in range(i, min(i + TOTAL_SIZE, len(b32)), SEGMENT_SIZE):
            k = min(j + SEGMENT_SIZE, i + TOTAL_SIZE, len(b32))
            name = f'{name}{b32[j:k].decode()}.'

        name = f'{name}{DOMAIN}'

        result.append(name)
        print(name)
    return result


def decode(names: list[str]) -> bytes:
    b32 = ''.join([name.rstrip(DOMAIN).replace('.', '') for name in names])
    b32 = b32 + '=' * (-len(b32) % 8)
    data = base64.b32decode(b32)
    print(data)
    return data


input = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ.0123456789\n'*10+']'
names = encode(str.encode(input))
print()
data = decode(names)
print(data.decode())

# n = 30
# for i in range(0, n, TOTAL_SIZE):
#     for j in range(i, min(i + TOTAL_SIZE, n), SEGMENT_SIZE):
#         print(f'{j} {min(j + SEGMENT_SIZE, i + TOTAL_SIZE, n)}')
#     print()
