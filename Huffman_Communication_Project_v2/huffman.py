from __future__ import annotations

from dataclasses import dataclass
from collections import Counter
import heapq
from typing import Optional


@dataclass
class Node:
    frequency: int
    symbol: Optional[str] = None
    left: Optional["Node"] = None
    right: Optional["Node"] = None


def build_tree(text: str) -> Node:
    if not text:
        raise ValueError("Cannot build a Huffman tree from empty text.")

    counts = Counter(text)
    heap = []
    serial = 0

    for symbol, frequency in counts.items():
        heapq.heappush(heap, (frequency, serial, Node(frequency, symbol=symbol)))
        serial += 1

    if len(heap) == 1:
        return heap[0][2]

    while len(heap) > 1:
        f1, _, n1 = heapq.heappop(heap)
        f2, _, n2 = heapq.heappop(heap)
        parent = Node(f1 + f2, left=n1, right=n2)
        heapq.heappush(heap, (parent.frequency, serial, parent))
        serial += 1

    return heap[0][2]


def generate_codes(root: Node) -> dict[str, str]:
    codes: dict[str, str] = {}

    def walk(node: Node, prefix: str) -> None:
        if node.symbol is not None:
            # For a one-symbol message, use one bit so the encoded stream
            # remains meaningful.
            codes[node.symbol] = prefix or "0"
            return
        walk(node.left, prefix + "0")
        walk(node.right, prefix + "1")

    walk(root, "")
    return codes


def encode(text: str, codes: dict[str, str]) -> str:
    return "".join(codes[ch] for ch in text)


def decode(bits: str, codes: dict[str, str]) -> str:
    reverse = {code: symbol for symbol, code in codes.items()}
    out = []
    current = ""

    for bit in bits:
        if bit not in "01":
            raise ValueError("Bitstream contains a character other than 0 or 1.")
        current += bit
        if current in reverse:
            out.append(reverse[current])
            current = ""

    if current:
        raise ValueError("Incomplete Huffman code at end of bitstream.")

    return "".join(out)


def frequency_table(text: str) -> Counter:
    return Counter(text)
