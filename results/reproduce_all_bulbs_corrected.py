#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone reproducible script for GSMG Phase2 bulb + Cosmic Duality Chain 1/2/3/4.

No input files are required: p3.b64, sa.b64, p32b.b64, and cd.b64 are embedded below.
The script writes BOTH binary and text/hex/printable views for every bulb and every derived chain.

Corrected/expanded version:
  - keeps backend errors instead of silently swallowing them
  - saves byte-stat reports for every artifact
  - separates the unused 1-byte Chain3 mystery tail after the 1168-byte Chain4 blob
  - treats Chain4 as binary block material, not as readable text
  - generates controlled Chain4 +-7 experiments on the 35 x 32-byte blocks

Crypto backend priority:
  1) cryptography Python package, if installed
  2) pycryptodome, if installed
  3) openssl command line, if available

Run:
  python reproduce_all_bulbs_chain3_chain4_standalone.py
  python reproduce_all_bulbs_chain3_chain4_standalone.py output_folder
"""

from __future__ import annotations

import base64
import hashlib
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

P3_B64 = r"""
U2FsdGVkX18GKGYS1D7X7VjxWz6uUyPFszr8dVvtOIrJqioWHgT69JJnzJGDVOvF
QYWh5BEZxFPXmMq1cbyy3dVVDgLhF050xlDy2J5grtKw9jUOO4oFNRgoD+1dlukX
pd8ccg++kkXgE9mGBP6lQbukDiSjY4mnR2Mv6ydIncrRqacQNVEmEgM4fGTi1ANz
nHsGn7mP+P3UyrJCRbuFmpZJc4CNdPj6YuxwR4HkHkqcfxh0L5CaEu4VbY70+fmk
qgZQyMJqiUlaV9KC4UPuRVj0r7MYbVRazkhsjeIcogmdJGEeBwD47lEB7X9PNKWm
ojTvRZg6R+sZzRZE26VLaF+s9cpTo4Y8PZUxKvQ86HXC8QIavUgDfw7HxIxkTatv
CW2yq3ZOXl5naR6oSNxdX9alyhTzB+/2623oGdlWev5Oo8xHJqUi7QjVP+mNC8BA
+Cg0DJwcOFGO5K7g8Rm06+sLogwntdIgTo70X3FegAtipHboeUNKefiAguvkDoIf
8iMPc+83PygvlZPDNQCOKugwDEUimhHwQrMsmalRNoFEQEb+ZIC+na15cPoRAlOD
NJfXIJ96ihAy9wWis39mQW6JFqZmUags4xoP3lJ35bCrXsNOPFZ4WH+f4YC/Ov8C
QW5bjtxno8GG4b/wBWevhcRVMK6KmRJj8NBCssnrlz0sQ70rMNkiN2wiSPcwX3Ad
JgLs8vQAUM59x9fkKFFzD4+Sc1sJztUTB7CMGGfpZOA8W33VZnEdmGcoaHlDsR8G
vAkZ+jg+QJs9ZNHqWE1+1zgm/6NsWWgWH8OI2PPCfXHxDbfDk8uD/Zibr/yjSKvu
Sb8OecflOT2hw37WL49uADgeWgnp2bzkfGIq7EYS7OImjZZwY5h4sfcPfhvQ9kOV
"""

SA_B64 = r"""
U2FsdGVkX186tYU0hVJBXXUnBUO7C0+X4KUWnWkCvoZSxbRD3wNsGWVHefvdrd9z
QvX0t8v3jPB4okpspxebRi6sE1BMl5HI8Rku+KejUqTvdWOX6nQjSpepXwGuN/jJ
"""

P32B_B64 = r"""
U2FsdGVkX1+0Wl49gnWTyiimluu7V3+vl7st0gUt9sWDzNLxDmlPMsDSiuW2a46z
gKlIi8aaqY5gpJPPEzW1n9n3/26qs4zstWtPKF8Zs/BTNN4IiEh4qu18mdC0NAv4
"""

CD_B64 = r"""
U2FsdGVkX18tP2/gbclQ5tNZuD4shoV3axuUd8J8aycGCAMoYfhZK0JecHTDpTFe
dGJh4SJIP66qRtXvo7PTpvsIjwO8prLiC/sNHthxiGMuqIrKoO224rOisFJZgARi
c7PaJPne4nab8XCFuV3NbfxGX2BUjNkef5hg7nsoadZx08dNyU2b6eiciWiUvu7D
SATSFO7IFBiAMz7dDqIETKuGlTAP4EmMQUZrQNtfbJsURATW6V5VSbtZB5RFk0O+
IymhstzrQHsU0Bugjv2nndmOEhCxGi/lqK2rLNdOOLutYGnA6RDDbFJUattggELh
2SZx+SBpCdbSGjxOap27l9FOyl02r0HU6UxFdcsbfZ1utTqVEyNs91emQxtpgt+6
BPZisil74Jv4EmrpRDC3ufnkmWwR8NfqVPIKhUiGDu5QflYjczT6DrA9vLQZu3ko
k+/ZurtRYnqqsj49UhwEF9GfUfl7uQYm0UunatW43C3Z1tyFRGAzAHQUFS6jRCd+
vZGyoTlOsThjXDDCSAwoX2M+yM+oaEQoVvDwVkIqRhfDNuBmEfi+HpXuJLPBS1Pb
UjrgoG/Uv7o8IeyST4HBv8+5KLx7IKQS8f1kPZ2YUME+8XJx0caFYs+JS2Jdm0oj
Jm3JJEcYXdKEzOQvRzi4k+6dNlJ05TRZNTJvn0fPG5cM80aQb/ckUHsLsw9a4Wzh
HsrzBQRTIhog9sTm+k+LkXzIJiFfSzRgf250pbviFGoQaIFl1CTQPT2w29DLP900
6bSiliywwnxXOor03Hn+7MJL27YxeaGQn0sFGgP5X0X4jm3vEBkWvtF4PZl0bXWZ
LvVL/zTn87+2Zi/u7LA6y6b2yt7YVMkpheeOL0japXaiAf3bSPeUPGz/eu8ZX/Nn
O3259hG1XwoEVcGdDBV0Nh0A4/phPCR0x5BG04U0OeWAT/5Udc/gGM0TT2FrEzs/
AJKtmsnj31OSsqWb9wD+CoduYY2JrkzJYihE3ZcgcvqqffZXqxQkaI/83ro6JZ4P
ubml0PUnAnkdmnBCpbClbZMzmo3ELZ0EQwsvkJFDMQmiRhda4nBooUW7zXOIb7Wx
bE9THrt3cdZP5uAgVfgguUNE4fZMN8ATEDhdSsLklJe2GvihKuZVA6uuSkWAsK6u
MGo76xpPwYs3eUdLjtANS83a6/F/fhkX1GXs7zbQjh+Inzk8jhEdEogl9jPs/oDj
KjbkUpFlsCWwAZGoeKlmX7c4OGuD5c+FEH+2nYHvYl8y1E/K5SDt9Uocio8XuxbD
ZOzhw7LMSGkD1MZxpDzsCZY1emkSNd88NFj+9U8VssIDDVMYwKMsHKfjc0x5OlzQ
1f6ST0xCkwydDHHGRKKxFC4y6H6fV9sgf9OPK/65z94Rx72+mfvTyizShjxYSRpl
sH9otU4parl8roD0KsVTfXZoYrYXzK6cXBn1BO/OEqWlu++Dd9MiGaUGKd22fXER
qNWoRAKlNn2b6EehD2D8WaAoliPURjkB0Lb/FpP9unI93Twg6NxBXAj734nctukR
b3kE08RydJV70eJsvEftF5hbED4HacGx9pzisaSz6t9AKiuSoF6uoCtlTIYatyfZ
kQA4wg50hAJqTynOQ09ArRHEchtB/7uvWZSBGJ7+zlzRGKx99P3oDZD+Y5D8bmUs
3PV6FnAp+IRSlnsQ6hChkwBoQUcngcfGSkBRvmGjsGercCetRRwBOfh9fbX2ruw4
mzRYrGnz9eBtepkJXDRjD6yvhNfQMCSkm6l9zMWxKvFbv5g2ae2SLrEt/x3MP2/G
"""

MASK = bytes.fromhex("b657264f2f6e6921")

TOKENS_CD = [
    "matrixsumlist",
    "enter",
    "lastwordsbeforearchichoice",
    "thispassword",
    "matrixsumlist",
    "yourlastcommand",
    "secondanswer",
]

# P3/Phase 2: OpenSSL AES-256-CBC with EVP_BytesToKey/SHA256 and passphrase equal
# to the ASCII hex string of SHA256("causality").
PASS_P3 = hashlib.sha256(b"causality").hexdigest().encode("ascii")

# SA/Chain 1: OpenSSL AES-256-CBC with EVP_BytesToKey/MD5.
PASS_SA = b"matrixsumlistenterlastwordsbeforearchichoicethispasswordmatrixsumlist"

EXPECTED = {
    "p3_sha256": "e2f9dd65604a3231f8b3301724e8d713a88fffc4b6c7c4aeeb20f58a582b593a",
    "chain3_sha256": "4f7a1e4efe4bf6c5581e32505c019657cb7b030e90232d33f011aca6a5e9c081",
    "chain4_sha256": "e4269ed5fbb202a81e5e1aa6b5190fdd1ea126b2c8547ea7cdbdf45387ea135b",
    "p3_len": 648,
    "chain1_len": 79,
    "chain2_len": 79,
    "chain3_len": 1327,
    "chain4_len": 1151,
    "chain4_header28": "ca9ebcdc7722e80ab9aa8bb166ab2cc79c2fef75ce3c638f45b3e705",
}

B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

BACKEND_LOG: List[str] = []


def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def sha256hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    h = 0.0
    n = len(data)
    for c in counts:
        if c:
            p = c / n
            h -= p * math.log2(p)
    return h



def printable_ratio(data: bytes) -> float:
    """Ratio of bytes that are normally printable ASCII, counting \r/\n/\t as text-like."""
    if not data:
        return 0.0
    good = sum(1 for x in data if 32 <= x <= 126 or x in (9, 10, 13))
    return good / len(data)


def ascii_preview(data: bytes, limit: int = 160) -> str:
    """Short escaped preview safe for reports."""
    view = printable_view(data[:limit])
    return view + ("..." if len(data) > limit else "")


def byte_stats_lines(name: str, data: bytes) -> List[str]:
    zeros = data.count(0)
    high = sum(1 for x in data if x >= 128)
    return [
        f"name = {name}",
        f"len = {len(data)}",
        f"sha256 = {sha256hex(data)}",
        f"entropy = {entropy(data):.6f}",
        f"printable_ratio = {printable_ratio(data):.6f}",
        f"zero_ratio = {(zeros / len(data) if data else 0.0):.6f}",
        f"high_byte_ratio = {(high / len(data) if data else 0.0):.6f}",
        f"preview = {ascii_preview(data)}",
    ]


def save_stats(outdir: Path, name: str, data: bytes) -> None:
    (outdir / f"{name}.stats.txt").write_text("\n".join(byte_stats_lines(name, data)) + "\n", encoding="utf-8")

def b58encode(b: bytes) -> str:
    n = int.from_bytes(b, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = B58[r] + out
    pad = len(b) - len(b.lstrip(b"\x00"))
    return "1" * pad + out


def b58check(payload: bytes) -> str:
    chk = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return b58encode(payload + chk)


def xor_many(items: Iterable[bytes]) -> bytes:
    items = list(items)
    if not items:
        raise ValueError("xor_many needs at least one item")
    out = bytearray(items[0])
    for b in items[1:]:
        if len(b) != len(out):
            raise ValueError("all XOR inputs must have the same length")
        for i, x in enumerate(b):
            out[i] ^= x
    return bytes(out)


def clean_b64(s: str) -> str:
    return "".join(s.split())


def decode_openssl_salted_b64(s: str) -> Tuple[bytes, bytes, bytes]:
    raw = base64.b64decode(clean_b64(s))
    if not raw.startswith(b"Salted__"):
        raise ValueError("not OpenSSL salted data; missing Salted__ prefix")
    return raw[8:16], raw[16:], raw


def evp_bytes_to_key(passphrase: bytes, salt: bytes, digest_name="md5", key_len=32, iv_len=16) -> Tuple[bytes, bytes]:
    """OpenSSL-compatible EVP_BytesToKey, one iteration."""
    out = b""
    prev = b""
    while len(out) < key_len + iv_len:
        h = hashlib.new(digest_name)
        h.update(prev + passphrase + salt)
        prev = h.digest()
        out += prev
    return out[:key_len], out[key_len:key_len + iv_len]


def pkcs7_unpad(data: bytes, block_size=16) -> bytes:
    if not data or len(data) % block_size:
        raise ValueError("invalid padded data length")
    pad = data[-1]
    if pad < 1 or pad > block_size:
        raise ValueError(f"invalid PKCS#7 padding byte: {pad}")
    if data[-pad:] != bytes([pad]) * pad:
        raise ValueError("invalid PKCS#7 padding bytes")
    return data[:-pad]


def aes256cbc_decrypt_nopad(ct: bytes, key: bytes, iv: bytes) -> bytes:
    """Decrypt AES-256-CBC without unpadding, using any available backend.

    The older version silently ignored backend failures. This version records
    them in BACKEND_LOG so crypto/environment problems are not hidden.
    """
    errors: List[str] = []

    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        dec = cipher.decryptor()
        BACKEND_LOG.append("AES backend used: cryptography")
        return dec.update(ct) + dec.finalize()
    except Exception as exc:
        errors.append(f"cryptography failed: {type(exc).__name__}: {exc}")

    try:
        from Crypto.Cipher import AES
        BACKEND_LOG.append("AES backend used: pycryptodome")
        return AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
    except Exception as exc:
        errors.append(f"pycryptodome failed: {type(exc).__name__}: {exc}")

    openssl_path = shutil.which("openssl")
    if openssl_path:
        proc = subprocess.run(
            [openssl_path, "enc", "-d", "-aes-256-cbc", "-K", key.hex(), "-iv", iv.hex(), "-nopad"],
            input=ct,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode == 0:
            BACKEND_LOG.append("AES backend used: openssl CLI")
            return proc.stdout
        errors.append("openssl CLI failed: " + proc.stderr.decode(errors="replace"))
    else:
        errors.append("openssl CLI not found")

    raise RuntimeError("No AES backend succeeded.\n" + "\n".join(errors))

def decrypt_openssl_salted_raw(raw: bytes, passphrase: bytes, digest_name="md5") -> bytes:
    if not raw.startswith(b"Salted__"):
        raise ValueError("raw blob does not start with Salted__")
    salt, ct = raw[8:16], raw[16:]
    key, iv = evp_bytes_to_key(passphrase, salt, digest_name=digest_name)
    padded = aes256cbc_decrypt_nopad(ct, key, iv)
    return pkcs7_unpad(padded)


def printable_view(data: bytes) -> str:
    return "".join(chr(x) if 32 <= x <= 126 else f"\\x{x:02x}" for x in data)


def best_text(data: bytes) -> str:
    """UTF-8 if possible, otherwise printable escaped view."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return printable_view(data)


def save_views(outdir: Path, name: str, data: bytes, *, include_b64: bool = True) -> None:
    """Save a binary blob plus several human-readable .txt views and stats."""
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / f"{name}.bin").write_bytes(data)
    (outdir / f"{name}.hex.txt").write_text(data.hex() + "\n", encoding="utf-8")
    (outdir / f"{name}.printable.txt").write_text(printable_view(data) + "\n", encoding="utf-8")
    (outdir / f"{name}.text_best_effort.txt").write_text(best_text(data) + "\n", encoding="utf-8", errors="replace")
    save_stats(outdir, name, data)
    if include_b64:
        b64 = base64.b64encode(data).decode("ascii")
        wrapped = "\n".join(b64[i:i+76] for i in range(0, len(b64), 76))
        (outdir / f"{name}.base64.txt").write_text(wrapped + "\n", encoding="utf-8")


def save_embedded_bulb(outdir: Path, name: str, b64_text: str) -> bytes:
    raw = base64.b64decode(clean_b64(b64_text))
    wrapped_input = "\n".join(clean_b64(b64_text)[i:i+76] for i in range(0, len(clean_b64(b64_text)), 76))
    (outdir / f"{name}.input.b64.txt").write_text(wrapped_input + "\n", encoding="utf-8")
    save_views(outdir, f"{name}.salted_raw", raw)
    salt = raw[8:16] if raw.startswith(b"Salted__") else b""
    meta = [
        f"name = {name}",
        f"raw_len = {len(raw)}",
        f"sha256_raw = {sha256hex(raw)}",
        f"is_openssl_salted = {raw.startswith(b'Salted__')}",
        f"salt = {salt.hex()}",
        f"ciphertext_len = {len(raw) - 16 if raw.startswith(b'Salted__') else 'n/a'}",
        f"entropy_raw = {entropy(raw):.6f}",
    ]
    (outdir / f"{name}.metadata.txt").write_text("\n".join(meta) + "\n", encoding="utf-8")
    return raw



def xor_bytes(a: bytes, b: bytes) -> bytes:
    if len(a) != len(b):
        raise ValueError("xor_bytes length mismatch")
    return bytes(x ^ y for x, y in zip(a, b))


def add_bytes(a: bytes, b: bytes) -> bytes:
    if len(a) != len(b):
        raise ValueError("add_bytes length mismatch")
    return bytes((x + y) & 0xff for x, y in zip(a, b))


def sub_bytes(a: bytes, b: bytes) -> bytes:
    if len(a) != len(b):
        raise ValueError("sub_bytes length mismatch")
    return bytes((x - y) & 0xff for x, y in zip(a, b))


def rotate_left_bytes(data: bytes, n: int) -> bytes:
    if not data:
        return data
    n %= len(data)
    return data[n:] + data[:n]


def rotate_right_bytes(data: bytes, n: int) -> bytes:
    if not data:
        return data
    n %= len(data)
    return data[-n:] + data[:-n] if n else data


def reduce_blocks(blocks: List[bytes], op_name: str) -> bytes:
    if not blocks:
        return b""
    out = blocks[0]
    for blk in blocks[1:]:
        if op_name == "xor":
            out = xor_bytes(out, blk)
        elif op_name == "add":
            out = add_bytes(out, blk)
        elif op_name == "sub":
            out = sub_bytes(out, blk)
        else:
            raise ValueError(f"unknown reduce operation: {op_name}")
    return out


def save_experiment_candidate(exp_dir: Path, name: str, data: bytes, rows: List[str]) -> None:
    save_views(exp_dir, name, data, include_b64=False)
    rows.append(
        "\t".join([
            name,
            str(len(data)),
            sha256hex(data),
            f"{entropy(data):.6f}",
            f"{printable_ratio(data):.6f}",
            ascii_preview(data, 96).replace("\t", " ").replace("\n", "\\n"),
        ])
    )


def run_chain4_pm7_experiments(outdir: Path, blocks_blob: bytes, operand: bytes) -> None:
    """Generate bounded experiments suggested by Chain4 marker '+-' and operand '7'.

    This does NOT claim to solve the puzzle. It only writes controlled candidates
    that are useful for checking whether '+-' and '7' refer to block order,
    block-pair arithmetic, XOR, or per-block rotation.
    """
    if len(blocks_blob) % 32 != 0:
        raise ValueError("Chain4 block blob length is not divisible by 32")

    blocks = [blocks_blob[i:i + 32] for i in range(0, len(blocks_blob), 32)]
    nblocks = len(blocks)
    step = int(chr(operand[0])) if operand and chr(operand[0]).isdigit() else 7

    exp_dir = outdir / "chain4_pm7_experiments"
    exp_dir.mkdir(parents=True, exist_ok=True)
    rows = ["name\tlen\tsha256\tentropy\tprintable_ratio\tpreview"]

    # 1) Rotate block order by +7 / -7.
    save_experiment_candidate(exp_dir, "order_rotate_left_7_blocks", b"".join(blocks[step:] + blocks[:step]), rows)
    save_experiment_candidate(exp_dir, "order_rotate_right_7_blocks", b"".join(blocks[-step:] + blocks[:-step]), rows)

    # 2) Rotate bytes inside each 32-byte block by +7 / -7.
    save_experiment_candidate(exp_dir, "each_block_rotate_left_7_bytes", b"".join(rotate_left_bytes(b, step) for b in blocks), rows)
    save_experiment_candidate(exp_dir, "each_block_rotate_right_7_bytes", b"".join(rotate_right_bytes(b, step) for b in blocks), rows)

    # 3) Cyclic pair block[i] with block[i+7]. Keeps 35 output blocks.
    plus = [blocks[(i + step) % nblocks] for i in range(nblocks)]
    minus = [blocks[(i - step) % nblocks] for i in range(nblocks)]
    for direction, other in [("plus7", plus), ("minus7", minus)]:
        save_experiment_candidate(exp_dir, f"cyclic_xor_{direction}", b"".join(xor_bytes(a, b) for a, b in zip(blocks, other)), rows)
        save_experiment_candidate(exp_dir, f"cyclic_add_{direction}", b"".join(add_bytes(a, b) for a, b in zip(blocks, other)), rows)
        save_experiment_candidate(exp_dir, f"cyclic_sub_{direction}", b"".join(sub_bytes(a, b) for a, b in zip(blocks, other)), rows)
        save_experiment_candidate(exp_dir, f"cyclic_revsub_{direction}", b"".join(sub_bytes(b, a) for a, b in zip(blocks, other)), rows)

    # 4) Non-cyclic pair block[i] with block[i+7]. Gives 28 output blocks.
    pairs = [(blocks[i], blocks[i + step]) for i in range(nblocks - step)]
    save_experiment_candidate(exp_dir, "noncyclic_xor_i_i_plus7", b"".join(xor_bytes(a, b) for a, b in pairs), rows)
    save_experiment_candidate(exp_dir, "noncyclic_add_i_i_plus7", b"".join(add_bytes(a, b) for a, b in pairs), rows)
    save_experiment_candidate(exp_dir, "noncyclic_sub_i_i_plus7", b"".join(sub_bytes(a, b) for a, b in pairs), rows)
    save_experiment_candidate(exp_dir, "noncyclic_revsub_i_i_plus7", b"".join(sub_bytes(b, a) for a, b in pairs), rows)

    # 5) Collapse all 35 blocks to one 32-byte candidate.
    save_experiment_candidate(exp_dir, "reduce_xor_all_35_blocks", reduce_blocks(blocks, "xor"), rows)
    save_experiment_candidate(exp_dir, "reduce_add_all_35_blocks", reduce_blocks(blocks, "add"), rows)
    save_experiment_candidate(exp_dir, "reduce_sub_all_35_blocks", reduce_blocks(blocks, "sub"), rows)

    # 6) Wing-like split: 17 + pivot + 17. Save halves and basic pair ops.
    left17 = blocks[:17]
    pivot = blocks[17]
    right17 = blocks[18:]
    right17_rev = list(reversed(right17))
    save_experiment_candidate(exp_dir, "wing_left17", b"".join(left17), rows)
    save_experiment_candidate(exp_dir, "wing_pivot_block17", pivot, rows)
    save_experiment_candidate(exp_dir, "wing_right17", b"".join(right17), rows)
    save_experiment_candidate(exp_dir, "wing_right17_reversed", b"".join(right17_rev), rows)
    save_experiment_candidate(exp_dir, "wing_xor_left17_right17", b"".join(xor_bytes(a, b) for a, b in zip(left17, right17)), rows)
    save_experiment_candidate(exp_dir, "wing_xor_left17_reversed_right17", b"".join(xor_bytes(a, b) for a, b in zip(left17, right17_rev)), rows)
    save_experiment_candidate(exp_dir, "wing_add_left17_right17", b"".join(add_bytes(a, b) for a, b in zip(left17, right17)), rows)
    save_experiment_candidate(exp_dir, "wing_sub_left17_right17", b"".join(sub_bytes(a, b) for a, b in zip(left17, right17)), rows)

    (exp_dir / "candidate_summary.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")

def main() -> None:
    outdir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("gsmg_full_bulb_out")
    outdir.mkdir(parents=True, exist_ok=True)

    print("=== Reproduce GSMG all embedded bulbs + Chain 3/4 ===")
    print(f"Output directory: {outdir.resolve()}")

    # Save all embedded bulbs before decryption.
    p3_raw = save_embedded_bulb(outdir, "p3", P3_B64)
    sa_raw = save_embedded_bulb(outdir, "sa", SA_B64)
    p32b_raw = save_embedded_bulb(outdir, "p32b", P32B_B64)
    cd_raw = save_embedded_bulb(outdir, "cd", CD_B64)

    # P3 / Phase 2 bulb.
    p3 = decrypt_openssl_salted_raw(p3_raw, PASS_P3, digest_name="sha256")
    save_views(outdir, "p3.decrypted_phase2", p3)

    # Chain 1: SA blob.
    chain1 = decrypt_openssl_salted_raw(sa_raw, PASS_SA, digest_name="md5")
    if len(chain1) != EXPECTED["chain1_len"]:
        raise AssertionError(f"Chain1 length expected {EXPECTED['chain1_len']}, got {len(chain1)}")
    K_C1, K_C2, E_C = chain1[:32], chain1[32:64], chain1[64:79]
    wif_kc1 = b58check(b"\x80" + K_C1)  # uncompressed WIF
    save_views(outdir, "sa.decrypted_chain1_79", chain1)
    save_views(outdir, "chain1.K_C1", K_C1)
    save_views(outdir, "chain1.K_C2", K_C2)
    save_views(outdir, "chain1.E_C", E_C)

    # Chain 2: P32B blob, password = uncompressed WIF(K_C1).
    chain2 = decrypt_openssl_salted_raw(p32b_raw, wif_kc1.encode("ascii"), digest_name="md5")
    if len(chain2) != EXPECTED["chain2_len"]:
        raise AssertionError(f"Chain2 length expected {EXPECTED['chain2_len']}, got {len(chain2)}")
    K_S1, K_S2, E_S = chain2[:32], chain2[32:64], chain2[64:79]
    save_views(outdir, "p32b.decrypted_chain2_79", chain2)
    save_views(outdir, "chain2.K_S1", K_S1)
    save_views(outdir, "chain2.K_S2", K_S2)
    save_views(outdir, "chain2.E_S", E_S)

    # Chain 3: CD / Cosmic Duality, password = raw XOR of SHA256(7 tokens).
    cd_pass = xor_many([sha256(t.encode("utf-8")) for t in TOKENS_CD])
    chain3 = decrypt_openssl_salted_raw(cd_raw, cd_pass, digest_name="md5")
    if len(chain3) != EXPECTED["chain3_len"]:
        raise AssertionError(f"Chain3 length expected {EXPECTED['chain3_len']}, got {len(chain3)}")
    chain3_hash = sha256hex(chain3)
    save_views(outdir, "cd.decrypted_chain3_cosmic_correct_1327", chain3)
    save_views(outdir, "chain3.cd_pass_xor7sha256", cd_pass)

    K_B1 = chain3[0:32]
    K_B2 = chain3[32:64]
    E_B  = chain3[64:79]
    K_H1 = chain3[79:111]
    K_H2 = chain3[111:143]
    E_H  = chain3[143:158]
    mystery = chain3[158:]
    if len(mystery) != 1169:
        raise AssertionError(f"mystery length expected 1169, got {len(mystery)}")

    save_views(outdir, "chain3.K_B1", K_B1)
    save_views(outdir, "chain3.K_B2", K_B2)
    save_views(outdir, "chain3.E_B", E_B)
    save_views(outdir, "chain3.K_H1", K_H1)
    save_views(outdir, "chain3.K_H2", K_H2)
    save_views(outdir, "chain3.E_H", E_H)
    save_views(outdir, "chain3.mystery_1169", mystery)

    # Chain 4 hidden blob from Chain3.
    # The mystery region is 1169 bytes, but the OpenSSL salted blob consumes exactly
    # 1168 bytes. The last byte is intentionally preserved separately. In current
    # data it is 0x3a (':'), which may be a separator/delimiter.
    mystery_1168 = mystery[:1168]
    mystery_tail = mystery[1168:]
    save_views(outdir, "chain3.mystery_first_1168_for_chain4", mystery_1168)
    save_views(outdir, "chain3.mystery_tail_after_1168", mystery_tail)
    chain4_unmasked = bytes(x ^ MASK[i % len(MASK)] for i, x in enumerate(mystery_1168))
    if not chain4_unmasked.startswith(b"Salted__"):
        raise AssertionError("Chain4 unmasked blob does not start with Salted__")
    save_views(outdir, "chain4.unmasked_salted_1168", chain4_unmasked)

    chain4_pass = E_C + E_S + E_B[:2]
    chain4 = decrypt_openssl_salted_raw(chain4_unmasked, chain4_pass, digest_name="md5")
    if len(chain4) != EXPECTED["chain4_len"]:
        raise AssertionError(f"Chain4 length expected {EXPECTED['chain4_len']}, got {len(chain4)}")
    chain4_hash = sha256hex(chain4)
    save_views(outdir, "chain4.decrypted_1151", chain4)
    save_views(outdir, "chain4.pass_EC_ES_EB2", chain4_pass)

    marker = chain4[:2]
    header28 = chain4[2:30]
    operand = chain4[30:31]
    blocks = chain4[31:]
    save_views(outdir, "chain4.marker", marker)
    save_views(outdir, "chain4.header28", header28)
    save_views(outdir, "chain4.operand", operand)
    save_views(outdir, "chain4.blocks_35x32", blocks)

    # Save each 32-byte Chain4 block separately, useful for CyberChef/dCode/manual checks.
    blocks_dir = outdir / "chain4_blocks"
    blocks_dir.mkdir(exist_ok=True)
    for i in range(35):
        blk = blocks[i*32:(i+1)*32]
        save_views(blocks_dir, f"block_{i:02d}", blk)

    # Controlled next-step candidates suggested by Chain4 marker '+-' and operand '7'.
    run_chain4_pm7_experiments(outdir, blocks, operand)

    # Compact summary table for all principal artifacts.
    artifacts = [
        ("p3_salted_raw", p3_raw),
        ("p3_decrypted_phase2", p3),
        ("sa_salted_raw", sa_raw),
        ("sa_decrypted_chain1_79", chain1),
        ("p32b_salted_raw", p32b_raw),
        ("p32b_decrypted_chain2_79", chain2),
        ("cd_salted_raw", cd_raw),
        ("cd_decrypted_chain3_1327", chain3),
        ("chain4_unmasked_salted_1168", chain4_unmasked),
        ("chain4_decrypted_1151", chain4),
        ("chain3_mystery_first_1168_for_chain4", mystery_1168),
        ("chain3_mystery_tail_after_1168", mystery_tail),
        ("chain4_blocks_1120", blocks),
    ]
    table_lines = ["name\tlen\tsha256\tentropy"]
    for name, data in artifacts:
        table_lines.append(f"{name}\t{len(data)}\t{sha256hex(data)}\t{entropy(data):.6f}")
    (outdir / "all_artifacts_summary.tsv").write_text("\n".join(table_lines) + "\n", encoding="utf-8")

    report = f"""
=== OK: all embedded bulbs and Chain 1/2/3/4 reproduced ===

P3 / phase2:
  passphrase text = SHA256('causality').hexdigest()
  EVP digest      = sha256
  len             = {len(p3)}
  SHA256          = {sha256hex(p3)}
  expected        = {EXPECTED['p3_sha256']}

Chain1 / SA bulb:
  passphrase      = {PASS_SA.decode('ascii')}
  EVP digest      = md5
  len             = {len(chain1)}
  SHA256          = {sha256hex(chain1)}
  K_C1            = {K_C1.hex()}
  K_C2            = {K_C2.hex()}
  E_C             = {E_C.hex()}
  WIF(K_C1, uncompressed) = {wif_kc1}

Chain2 / P32B bulb:
  passphrase      = WIF(K_C1, uncompressed)
  EVP digest      = md5
  len             = {len(chain2)}
  SHA256          = {sha256hex(chain2)}
  K_S1            = {K_S1.hex()}
  K_S2            = {K_S2.hex()}
  E_S             = {E_S.hex()}

Chain3 / CD / cosmic_correct:
  pass raw hex    = {cd_pass.hex()}
  tokens          = {', '.join(TOKENS_CD)}
  len             = {len(chain3)}
  SHA256          = {chain3_hash}
  expected        = {EXPECTED['chain3_sha256']}
  K_B1            = {K_B1.hex()}
  K_B2            = {K_B2.hex()}
  E_B             = {E_B.hex()}
  K_H1            = {K_H1.hex()}
  K_H2            = {K_H2.hex()}
  E_H             = {E_H.hex()}
  mystery len     = {len(mystery)}
  mystery[0:1168] = used for Chain4 salted blob
  mystery tail    = {mystery_tail.hex()} / {mystery_tail!r}

Chain4:
  mask            = {MASK.hex()}
  unmasked salt   = {chain4_unmasked[8:16].hex()}
  pass raw hex    = {chain4_pass.hex()}
  len             = {len(chain4)}
  SHA256          = {chain4_hash}
  expected        = {EXPECTED['chain4_sha256']}
  marker          = {marker!r} / {marker.hex()}
  header28        = {header28.hex()}
  expected hdr    = {EXPECTED['chain4_header28']}
  operand         = 0x{operand[0]:02x} / {chr(operand[0])!r}
  blocks len      = {len(blocks)} = 35 * 32 ? {len(blocks) == 35 * 32}

Text/hex/printable outputs:
  For every bulb/artifact, this script writes:
    *.bin
    *.hex.txt
    *.printable.txt
    *.text_best_effort.txt
    *.base64.txt

Per-block Chain4 views are in:
  {(outdir / 'chain4_blocks').resolve()}

Controlled Chain4 +-7 experiments are in:
  {(outdir / 'chain4_pm7_experiments').resolve()}

AES backend log:
  {chr(10).join(BACKEND_LOG)}

Files written to:
  {outdir.resolve()}
""".strip() + "\n"
    print(report)
    (outdir / "reproduction_report.txt").write_text(report, encoding="utf-8")

    # Strong consistency checks.
    assert len(p3) == EXPECTED["p3_len"], "P3 length mismatch"
    assert sha256hex(p3) == EXPECTED["p3_sha256"], "P3 SHA256 mismatch"
    assert len(chain1) == EXPECTED["chain1_len"], "Chain1 length mismatch"
    assert len(chain2) == EXPECTED["chain2_len"], "Chain2 length mismatch"
    assert chain3_hash == EXPECTED["chain3_sha256"], "Chain3 SHA256 mismatch"
    assert chain4_hash == EXPECTED["chain4_sha256"], "Chain4 SHA256 mismatch"
    assert header28.hex() == EXPECTED["chain4_header28"], "Chain4 header mismatch"
    assert len(mystery_tail) == 1, "Expected a one-byte Chain3 mystery tail"


if __name__ == "__main__":
    main()
