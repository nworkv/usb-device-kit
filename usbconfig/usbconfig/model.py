from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal

Direction = Literal["in", "out"]
TransferType = Literal["control", "isochronous", "bulk", "interrupt"]

@dataclass
class SuperSpeedCompanion:
    max_burst: int = 0
    max_streams: int = 0
    mult: int = 0
    bytes_per_interval: int = 0

@dataclass
class Endpoint:
    number: int
    direction: Direction
    transfer_type: TransferType
    max_packet_size: int
    interval: int = 0
    synchronization: int = 0
    usage: int = 0
    superspeed: SuperSpeedCompanion | None = None
    raw: str | None = None
    @property
    def address(self): return self.number | (0x80 if self.direction == "in" else 0)

@dataclass
class RawDescriptor:
    attach_to: str = "interface"
    bytes_hex: str = ""
    @property
    def data(self):
        from .binary import parse_hex
        return parse_hex(self.bytes_hex)

@dataclass
class HIDFunction:
    bcd_hid: str = "0x0111"
    country_code: int = 0
    report_descriptor_hex: str = ""
    @property
    def report_descriptor(self):
        from .binary import parse_hex
        return parse_hex(self.report_descriptor_hex)

@dataclass
class Interface:
    number: int
    alternate_setting: int = 0
    interface_class: int = 0xFF
    interface_subclass: int = 0
    interface_protocol: int = 0
    interface_index: int = 0
    class_specific: list = field(default_factory=list)
    endpoints: list = field(default_factory=list)

@dataclass
class InterfaceAssociation:
    first_interface: int
    interface_count: int
    function_class: int
    function_subclass: int = 0
    function_protocol: int = 0
    function_index: int = 0

@dataclass
class Configuration:
    name: str = "Default"
    configuration_value: int = 1
    self_powered: bool = False
    remote_wakeup: bool = False
    max_power_ma: int = 500
    configuration_index: int = 0
    interfaces: list = field(default_factory=list)
    associations: list = field(default_factory=list)
    class_specific: list = field(default_factory=list)
    vendor_specific: list = field(default_factory=list)

@dataclass
class StringSet:
    languages: list = field(default_factory=lambda: [0x0409])
    manufacturer: str = ""
    product: str = ""
    serial: str = ""
    extra: dict = field(default_factory=dict)

@dataclass
class Usb2ExtensionCapability:
    lpm_capable: bool = True
    bcd_usb: str = "0x0200"

@dataclass
class SuperSpeedCapability:
    ltm_capable: bool = False
    speeds_supported: int = 0x08
    functionality_support: int = 3
    u1_exit_latency: int = 1
    u2_exit_latency: int = 250

@dataclass
class BOS:
    usb2_extension: Usb2ExtensionCapability | None = None
    superspeed: SuperSpeedCapability | None = None
    raw_capabilities: list = field(default_factory=list)

@dataclass
class Device:
    bcd_usb: str = "0x0200"
    device_class: int = 0
    device_subclass: int = 0
    device_protocol: int = 0
    vendor_id: int = 0
    product_id: int = 0
    bcd_device: str = "0x0100"
    max_packet_size_ep0: int = 64
    strings: StringSet = field(default_factory=StringSet)
    configurations: list = field(default_factory=list)
    bos: BOS | None = None
    class_specific: list = field(default_factory=list)
    vendor_specific: list = field(default_factory=list)
    @property
    def bcd_usb_value(self): return int(self.bcd_usb, 0)
    @property
    def bcd_device_value(self): return int(self.bcd_device, 0)
