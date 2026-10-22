from __future__ import annotations
import math
from .binary import descriptor, u8, u16, u32, utf16le
from .model import BOS, Configuration, Device, Endpoint, HIDFunction, Interface, InterfaceAssociation, SuperSpeedCompanion
DEVICE=0x01; CONFIGURATION=0x02; STRING=0x03; INTERFACE=0x04; ENDPOINT=0x05
DEVICE_QUALIFIER=0x06; OTHER_SPEED_CONFIGURATION=0x07; INTERFACE_ASSOCIATION=0x0B
BOS=0x0F; DEVICE_CAPABILITY=0x10; SS_EP_COMPANION=0x30
TRANSFER={"control":0,"isochronous":1,"bulk":2,"interrupt":3}
def build_device_descriptor(d: Device):
    return descriptor(DEVICE, u16(d.bcd_usb_value)+u8(d.device_class)+u8(d.device_subclass)+u8(d.device_protocol)
        +u8(int(math.log2(d.max_packet_size_ep0)))+u16(d.vendor_id)+u16(d.product_id)+u16(d.bcd_device_value)
        +u8(1 if d.strings.manufacturer else 0)+u8(1 if d.strings.product else 0)+u8(1 if d.strings.serial else 0)
        +u8(len(d.configurations)))
def build_device_qualifier(d: Device):
    return descriptor(DEVICE_QUALIFIER, u16(0x0200)+u8(d.device_class)+u8(d.device_subclass)+u8(d.device_protocol)+u8(64)+u8(len(d.configurations))+u8(0))
def build_string_descriptor(index, text, languages):
    if index == 0: return descriptor(STRING, b"".join(u16(x) for x in languages))
    if text is None: raise ValueError("empty string")
    return descriptor(STRING, utf16le(text))
def build_bos(bos: BOS):
    caps, count = b"", 0
    if bos.usb2_extension:
        caps += descriptor(DEVICE_CAPABILITY, u8(0x02)+u32(0x02 if bos.usb2_extension.lpm_capable else 0)); count += 1
    if bos.superspeed:
        caps += descriptor(DEVICE_CAPABILITY, u8(0x03)+u8(0x01 if bos.superspeed.ltm_capable else 0)
            +u16(bos.superspeed.speeds_supported)+u8(bos.superspeed.functionality_support)
            +u8(bos.superspeed.u1_exit_latency)+u16(bos.superspeed.u2_exit_latency)); count += 1
    for raw in bos.raw_capabilities: caps += raw.data; count += 1
    return descriptor(BOS, u16(len(caps)+5)+u8(count))+caps
def build_iad(iad): return descriptor(INTERFACE_ASSOCIATION, u8(iad.first_interface)+u8(iad.interface_count)+u8(iad.function_class)+u8(iad.function_subclass)+u8(iad.function_protocol)+u8(iad.function_index))
def build_interface(i: Interface): return descriptor(INTERFACE, u8(i.number)+u8(i.alternate_setting)+u8(len(i.endpoints))+u8(i.interface_class)+u8(i.interface_subclass)+u8(i.interface_protocol)+u8(i.interface_index))
def build_hid_descriptor(hid: HIDFunction): return descriptor(0x21, u16(int(hid.bcd_hid,0))+u8(hid.country_code)+u8(1)+u8(0x22)+u16(len(hid.report_descriptor)))
def build_endpoint(ep: Endpoint):
    attrs = TRANSFER[ep.transfer_type]
    if ep.transfer_type == "isochronous": attrs |= (ep.synchronization & 3) << 2 | (ep.usage & 3) << 4
    return descriptor(ENDPOINT, u8(ep.address)+u8(attrs)+u16(ep.max_packet_size)+u8(ep.interval))
def build_ss_companion(c: SuperSpeedCompanion, transfer_type):
    attrs = c.max_streams & 0x1F if transfer_type == "bulk" else ((c.mult & 3) | 0x04 if transfer_type == "isochronous" else 0)
    return descriptor(SS_EP_COMPANION, u8(c.max_burst)+u8(attrs)+u16(c.bytes_per_interval))
def build_configuration_block(config: Configuration, usb3=True, descriptor_type=CONFIGURATION):
    body = b""
    associations = {x.first_interface: x for x in config.associations}
    for iface in config.interfaces:
        if iface.number in associations: body += build_iad(associations[iface.number])
        body += build_interface(iface)
        hid = getattr(iface, "hid", None)
        if isinstance(hid, HIDFunction): body += build_hid_descriptor(hid)
        for raw in iface.class_specific: body += raw.data
        for ep in iface.endpoints:
            if ep.raw:
                from .binary import parse_hex
                body += parse_hex(ep.raw); continue
            body += build_endpoint(ep)
            if usb3 and ep.superspeed: body += build_ss_companion(ep.superspeed, ep.transfer_type)
    for raw in config.class_specific: body += raw.data
    for raw in config.vendor_specific: body += raw.data
    attrs = 0x80 | (0x40 if config.self_powered else 0) | (0x20 if config.remote_wakeup else 0)
    total = 9 + len(body)
    return u8(9)+u8(descriptor_type)+u16(total)+u8(len(config.interfaces))+u8(config.configuration_value)+u8(config.configuration_index)+u8(attrs)+u8(min(250, max(0, config.max_power_ma // 2))) + body
