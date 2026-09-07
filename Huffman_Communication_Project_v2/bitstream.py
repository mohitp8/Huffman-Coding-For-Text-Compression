from __future__ import annotations


def bits_to_bytes(bits: str) -> tuple[bytes, int]:
    if any(b not in "01" for b in bits):
        raise ValueError("Bitstream must contain only 0 and 1.")

    valid_bits = len(bits)
    if valid_bits == 0:
        return b"", 0

    padding = (-valid_bits) % 8
    padded = bits + ("0" * padding)

    data = bytes(
        int(padded[i:i + 8], 2)
        for i in range(0, len(padded), 8)
    )
    return data, valid_bits


def bytes_to_bits(data: bytes, valid_bits: int) -> str:
    if valid_bits < 0 or valid_bits > len(data) * 8:
        raise ValueError("Invalid valid_bits value.")

    all_bits = "".join(f"{byte:08b}" for byte in data)
    return all_bits[:valid_bits]
