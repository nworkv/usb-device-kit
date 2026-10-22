from __future__ import annotations
import json
from pathlib import Path
from .builder import *
from .loader import load_device
from .validator import validate_device
def generate(input_path, output_dir):
    device = load_device(input_path)
    validate_device(device)
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    files = {}
    def write(name, data):
        (out/name).write_bytes(data); return name
    files["1:0:0"] = write("01_device.bin", build_device_descriptor(device))
    files["6:0:0"] = write("06_device_qualifier.bin", build_device_qualifier(device))
    files["7:0:0"] = write("07_other_speed_configuration.bin", build_configuration_block(device.configurations[0], usb3=False, descriptor_type=OTHER_SPEED_CONFIGURATION))
    if device.bos: files["15:0:0"] = write("0F_bos.bin", build_bos(device.bos))
    langs = device.strings.languages
    files["3:0:0"] = write("03_string_0.bin", build_string_descriptor(0, None, langs))
    for i, text in ((1, device.strings.manufacturer), (2, device.strings.product), (3, device.strings.serial)):
        if text: files[f"3:{i}:0"] = write(f"03_string_{i}.bin", build_string_descriptor(i, text, langs))
    for i, text in device.strings.extra.items(): files[f"3:{i}:0"] = write(f"03_string_{i}.bin", build_string_descriptor(i, text, langs))
    for config in device.configurations:
        key = f"2:{config.configuration_value-1}:0"
        files[key] = write(f"02_configuration_{config.configuration_value-1}.bin", build_configuration_block(config, usb3=True))
    endpoints = {}
    for config in device.configurations:
        for iface in config.interfaces:
            for ep in iface.endpoints:
                if ep.raw: continue
                data = build_endpoint(ep)
                if ep.superspeed: data += build_ss_companion(ep.superspeed, ep.transfer_type)
                name = f"endpoint_0x{ep.address:02X}.bin"
                (out/name).write_bytes(data)
                endpoints[f"0x{ep.address:02X}"] = {"file": name, "type": ep.transfer_type, "direction": ep.direction, "max_packet_size": ep.max_packet_size}
    (out/"case.json").write_text(json.dumps({"id": Path(input_path).stem, "files": files, "endpoints": endpoints}, indent=2)+"\n")
    return out
