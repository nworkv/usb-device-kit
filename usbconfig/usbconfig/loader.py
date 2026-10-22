from __future__ import annotations
import json
from pathlib import Path
from .model import *
def _int(v, d=0):
    if v is None: return d
    return int(v, 0) if isinstance(v, str) else int(v)
def _raw(v, attach="interface"): return RawDescriptor(v.get("attach_to", attach), v["bytes_hex"])
def _endpoint(v):
    ss = v.get("superspeed") or v.get("superspeed_endpoint_companion")
    return Endpoint(
        number=_int(v["number"]), direction=v["direction"], transfer_type=v["transfer_type"],
        max_packet_size=_int(v["max_packet_size"]), interval=_int(v.get("interval", 0)),
        synchronization=_int(v.get("synchronization", 0)), usage=_int(v.get("usage", 0)),
        superspeed=None if ss is None else SuperSpeedCompanion(
            max_burst=_int(ss.get("max_burst", 0)), max_streams=_int(ss.get("max_streams", 0)),
            mult=_int(ss.get("mult", 0)), bytes_per_interval=_int(ss.get("bytes_per_interval", 0))),
        raw=v.get("bytes_hex"))
def _interface(v):
    return Interface(
        number=_int(v["interface_number"]), alternate_setting=_int(v.get("alternate_setting", 0)),
        interface_class=_int(v["interface_class"]), interface_subclass=_int(v.get("interface_subclass", 0)),
        interface_protocol=_int(v.get("interface_protocol", 0)), interface_index=_int(v.get("interface_index", 0)),
        class_specific=[_raw(x) for x in v.get("class_specific", [])],
        endpoints=[_endpoint(x) for x in v.get("endpoints", [])])
def _configuration(v):
    interfaces, associations = [], []
    for function in v.get("functions", []):
        if function.get("type") == "hid":
            iface = Interface(
                number=_int(function.get("interface_number", len(interfaces))),
                interface_class=0x03,
                interface_subclass=_int(function.get("interface_subclass", 0)),
                interface_protocol=_int(function.get("interface_protocol", 0)),
                interface_index=_int(function.get("interface_index", 0)),
                endpoints=[_endpoint(x) for x in function.get("endpoints", [])])
            iface.hid = HIDFunction(
                bcd_hid=function.get("hid", {}).get("bcd_hid", "0x0111"),
                country_code=_int(function.get("hid", {}).get("country_code", 0)),
                report_descriptor_hex=function.get("hid", {}).get("report_descriptor_hex", ""))
            interfaces.append(iface)
            associations.append(InterfaceAssociation(iface.number, 1, 0x03, iface.interface_subclass, iface.interface_protocol, iface.interface_index))
        else:
            raw_ifaces = function.get("interfaces", [])
            for ri in raw_ifaces: interfaces.append(_interface(ri))
            if len(raw_ifaces) > 1:
                associations.append(InterfaceAssociation(
                    _int(raw_ifaces[0]["interface_number"]), len(raw_ifaces),
                    _int(function.get("function_class", 0xFF)),
                    _int(function.get("function_subclass", 0)),
                    _int(function.get("function_protocol", 0)),
                    _int(function.get("function_index", 0))))
    for ri in v.get("interfaces", []): interfaces.append(_interface(ri))
    return Configuration(
        name=v.get("name", "Default"), configuration_value=_int(v.get("configuration_value", 1), 1),
        self_powered=bool(v.get("self_powered", False)), remote_wakeup=bool(v.get("remote_wakeup", False)),
        max_power_ma=_int(v.get("max_power_ma", 500)), configuration_index=_int(v.get("configuration_index", 0)),
        interfaces=interfaces, associations=associations,
        class_specific=[_raw(x, "configuration") for x in v.get("class_specific", [])],
        vendor_specific=[_raw(x, "configuration") for x in v.get("vendor_specific", [])])
def load_device(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    d = data["device"]
    strings = d.get("strings", {})
    bos_data = data.get("bos")
    bos = None
    if bos_data:
        usb2 = bos_data.get("usb2_extension")
        ss = bos_data.get("superspeed")
        bos = BOS(
            usb2_extension=None if usb2 is None else Usb2ExtensionCapability(
                bool(usb2.get("lpm_capable", True)), usb2.get("bcd_usb", "0x0200")),
            superspeed=None if ss is None else SuperSpeedCapability(
                bool(ss.get("ltm_capable", False)), _int(ss.get("speeds_supported", 0x08)),
                _int(ss.get("functionality_support", 3)), _int(ss.get("u1_exit_latency", 1)),
                _int(ss.get("u2_exit_latency", 250))),
            raw_capabilities=[_raw(x, "device") for x in bos_data.get("raw_capabilities", [])])
    return Device(
        bcd_usb=d.get("bcd_usb", "0x0200"), device_class=_int(d.get("device_class", 0)),
        device_subclass=_int(d.get("device_subclass", 0)), device_protocol=_int(d.get("device_protocol", 0)),
        vendor_id=_int(d["vendor_id"]), product_id=_int(d["product_id"]),
        bcd_device=d.get("bcd_device", "0x0100"), max_packet_size_ep0=_int(d.get("max_packet_size_ep0", 64)),
        strings=StringSet(
            languages=[_int(x, 0x0409) for x in strings.get("languages", [0x0409])],
            manufacturer=strings.get("manufacturer", ""), product=strings.get("product", ""),
            serial=strings.get("serial", ""), extra={_int(k): v for k, v in strings.get("extra", {}).items()}),
        configurations=[_configuration(x) for x in data.get("configurations", [])],
        bos=bos,
        class_specific=[_raw(x, "device") for x in d.get("class_specific", [])],
        vendor_specific=[_raw(x, "device") for x in d.get("vendor_specific", [])])
