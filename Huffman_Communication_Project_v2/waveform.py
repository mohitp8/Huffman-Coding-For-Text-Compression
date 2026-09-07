from __future__ import annotations

import matplotlib.pyplot as plt


def plot_nrz(bits: str, title: str = "Huffman Bitstream - NRZ-L Waveform",
             max_bits: int = 160) -> None:
    bits = bits[:max_bits]

    if not bits:
        raise ValueError("No bits to plot.")

    x = []
    y = []

    for i, bit in enumerate(bits):
        level = 1 if bit == "1" else -1
        x.extend([i, i + 1])
        y.extend([level, level])

    plt.figure(figsize=(12, 4))
    plt.step(x, y, where="post")
    plt.yticks([-1, 1], ["0", "1"])
    plt.xticks(range(len(bits) + 1))
    plt.xlabel("Bit interval")
    plt.ylabel("Logic level")
    plt.title(title)
    plt.grid(True, alpha=0.3)

    for i, bit in enumerate(bits):
        plt.text(i + 0.5, 1.18 if bit == "1" else -1.18, bit,
                 ha="center", va="center")

    plt.ylim(-1.5, 1.5)
    plt.tight_layout()
    plt.show()
