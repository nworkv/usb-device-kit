#!/usr/bin/env python3
import argparse, json, os
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument("case_json"); p.add_argument("-o", "--output", required=True)
a = p.parse_args()
case_path = Path(a.case_json).resolve()
case_dir = case_path.parent
output_path = Path(a.output).resolve()
output_dir = output_path.parent
case = json.loads(case_path.read_text())
files = case["files"]
lines = []
def add(key, filename):
    if filename:
        rel = os.path.relpath(case_dir / filename, output_dir)
        lines.append(f"{key} {rel}")
add("device", files.get("1:0:0"))
add("qualifier", files.get("6:0:0"))
add("other_config", files.get("7:0:0"))
add("bos", files.get("15:0:0"))
for i in range(16): add(f"string{i}", files.get(f"3:{i}:0"))
for i in range(16): add(f"config{i}", files.get(f"2:{i}:0"))
for address, endpoint in case.get("endpoints", {}).items():
    number = int(address, 16) & 0x0F
    transfer = {"control":0,"isochronous":1,"bulk":2,"interrupt":3}[endpoint["type"]]
    attrs = transfer | (0x04 if transfer == 1 else 0)
    lines.append(f"endpoint {number} {endpoint['direction']} {attrs} {endpoint['max_packet_size']} 0")
output_path.write_text("\n".join(lines)+"\n")
print(f"Written: {output_path}")
