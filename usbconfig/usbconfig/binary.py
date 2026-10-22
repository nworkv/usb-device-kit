from __future__ import annotations
import struct
def u8(v):
    if not 0 <= v <= 0xFF: raise ValueError("u8 out of range")
    return struct.pack("<B", v)
def u16(v):
    if not 0 <= v <= 0xFFFF: raise ValueError("u16 out of range")
    return struct.pack("<H", v)
def u32(v):
    if not 0 <= v <= 0xFFFFFFFF: raise ValueError("u32 out of range")
    return struct.pack("<I", v)
def descriptor(t, payload): return u8(len(payload)+2) + u8(t) + payload
def utf16le(text): return text.encode("utf-16-le")
def parse_hex(value):
    if isinstance(value, bytes): return value
    cleaned = value.replace(" ", "").replace("\n", "")
    if cleaned.startswith("0x"): cleaned = cleaned[2:]
    if len(cleaned) % 2: raise ValueError("hex must have even length")
    return bytes.fromhex(cleaned)
