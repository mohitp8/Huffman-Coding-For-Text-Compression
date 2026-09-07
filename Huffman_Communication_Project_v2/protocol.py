from __future__ import annotations

import struct
import zlib


MAGIC = b"HUF1"
VERSION = 1

# Header:
# magic(4), version(1), symbol_count(2), original_chars(4),
# valid_bits(4), data_length(4)
HEADER = struct.Struct("!4sB H I I I")

# Each codebook entry:
# UTF-8 symbol length(2), code length(2), UTF-8 symbol bytes, code bytes as ASCII
ENTRY_HEAD = struct.Struct("!H H")


def serialize_codebook(codebook: dict[str, str]) -> bytes:
    payload = bytearray()

    for symbol, code in sorted(codebook.items(), key=lambda x: x[0]):
        symbol_bytes = symbol.encode("utf-8")
        code_bytes = code.encode("ascii")
        payload += ENTRY_HEAD.pack(len(symbol_bytes), len(code_bytes))
        payload += symbol_bytes
        payload += code_bytes

    return bytes(payload)


def deserialize_codebook(data: bytes, symbol_count: int) -> tuple[dict[str, str], int]:
    offset = 0
    codebook: dict[str, str] = {}

    for _ in range(symbol_count):
        if offset + ENTRY_HEAD.size > len(data):
            raise ValueError("Truncated Huffman codebook.")

        symbol_len, code_len = ENTRY_HEAD.unpack_from(data, offset)
        offset += ENTRY_HEAD.size

        if offset + symbol_len + code_len > len(data):
            raise ValueError("Truncated Huffman codebook entry.")

        symbol = data[offset:offset + symbol_len].decode("utf-8")
        offset += symbol_len

        code = data[offset:offset + code_len].decode("ascii")
        offset += code_len

        if symbol in codebook:
            raise ValueError("Duplicate symbol in codebook.")
        codebook[symbol] = code

    return codebook, offset


def build_frame(codebook: dict[str, str], original_chars: int,
                compressed_data: bytes, valid_bits: int) -> bytes:
    table = serialize_codebook(codebook)
    crc = zlib.crc32(table + compressed_data) & 0xFFFFFFFF

    header = HEADER.pack(
        MAGIC,
        VERSION,
        len(codebook),
        original_chars,
        valid_bits,
        len(compressed_data),
    )

    return header + table + compressed_data + struct.pack("!I", crc)


def parse_frame(frame: bytes):
    if len(frame) < HEADER.size + 4:
        raise ValueError("Frame is too short.")

    magic, version, symbol_count, original_chars, valid_bits, data_length = HEADER.unpack_from(frame)

    if magic != MAGIC:
        raise ValueError("Invalid frame magic.")
    if version != VERSION:
        raise ValueError("Unsupported protocol version.")

    table_start = HEADER.size
    codebook, table_len = deserialize_codebook(
        frame[table_start:], symbol_count
    )

    data_start = table_start + table_len
    data_end = data_start + data_length

    if data_end + 4 != len(frame):
        raise ValueError("Frame length does not match header.")

    compressed_data = frame[data_start:data_end]
    received_crc = struct.unpack("!I", frame[data_end:data_end + 4])[0]
    calculated_crc = zlib.crc32(
        frame[table_start:data_end]
    ) & 0xFFFFFFFF

    if received_crc != calculated_crc:
        raise ValueError("CRC verification failed.")

    return {
        "codebook": codebook,
        "original_chars": original_chars,
        "valid_bits": valid_bits,
        "compressed_data": compressed_data,
        "crc_ok": True,
    }


def send_all(sock, data: bytes) -> None:
    sock.sendall(struct.pack("!I", len(data)))
    sock.sendall(data)


def receive_exact(sock, n: int) -> bytes:
    chunks = []
    remaining = n

    while remaining:
        chunk = sock.recv(min(65536, remaining))
        if not chunk:
            raise ConnectionError("Connection closed before complete frame arrived.")
        chunks.append(chunk)
        remaining -= len(chunk)

    return b"".join(chunks)


def receive_frame(sock) -> bytes:
    length_bytes = receive_exact(sock, 4)
    frame_length = struct.unpack("!I", length_bytes)[0]

    if frame_length <= 0 or frame_length > 50 * 1024 * 1024:
        raise ValueError("Invalid frame length.")

    return receive_exact(sock, frame_length)
