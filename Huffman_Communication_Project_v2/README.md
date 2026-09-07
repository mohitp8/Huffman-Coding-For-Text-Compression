# Huffman-Based Lossless Text Compression and Real-Time Digital Communication

## Project
Two-laptop Python project:
1. Enter text on Laptop 1.
2. Build a Huffman tree and code table.
3. Compress the text into a bitstream.
4. Pack the bits into bytes.
5. Build a framed TCP message containing the Huffman codebook and compressed data.
6. Transmit the frame to Laptop 2 over the same Wi-Fi/LAN.
7. Receive, unpack, reconstruct the codebook, and Huffman-decode.
8. Verify the received message.
9. Display the logical compressed bitstream as an NRZ waveform.

## Requirements
Python 3.10+ recommended.

Install:
```bash
pip install matplotlib
```

Tkinter is normally included with standard Python on Windows. If Python was installed without Tk support, reinstall Python with the standard Tcl/Tk option.

## Files
- `huffman.py` - Huffman tree, code generation, encoding and decoding
- `bitstream.py` - bit/byte packing and unpacking
- `protocol.py` - binary communication frame
- `waveform.py` - NRZ waveform plotting
- `sender_gui.py` - Laptop 1 transmitter GUI
- `receiver_gui.py` - Laptop 2 receiver GUI

## How to run

### Laptop 2 first
Run:
```bash
python receiver_gui.py
```

The receiver listens on TCP port 5000.

Find Laptop 2's local IP address:
```bash
ipconfig
```
Look for the IPv4 address of the Wi-Fi adapter, for example:
`192.168.1.25`

### Laptop 1
Edit nothing if the receiver uses port 5000. Run:
```bash
python sender_gui.py
```

Enter Laptop 2's IP address, enter a message, click `Compress`, then `Send`.

## Important
The waveform shown by this project is a logical NRZ representation of the Huffman bitstream. It is NOT the physical Wi-Fi waveform. Wi-Fi uses its own physical-layer modulation and coding.

## Recommended demonstration
Use a reasonably long, repetitive sentence so Huffman compression is clearly visible. Very short messages can have poor total compression because the codebook/header adds overhead.

## Future enhancements
- Manchester waveform option
- Canonical Huffman codebook
- CRC-32 validation
- Transfer history
- File compression
- Real serial/USB-UART hardware mode
