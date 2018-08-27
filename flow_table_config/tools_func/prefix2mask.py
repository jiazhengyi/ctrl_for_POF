
def generate_mask_string(size, length):
    if 64 == size:
        i = (0xFFFFFFFFFFFFFFFF << (size - length)) & 0xFFFFFFFFFFFFFFFF
    elif 32 == size:
        i = (0xFFFFFFFF << (size - length)) & 0xFFFFFFFF
    elif 16 == size:
        i = (0xFFFF << (size - length)) & 0xFFFF
    elif 8 == size:
        i = (0xFF << (size - length)) & 0xFF
    else:
        assert 0
    return "%x" % i

for i in range(1, 32):
    print generate_mask_string(32, i)
