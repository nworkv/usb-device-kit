from .model import Device
class UsbConfigError(ValueError): pass
def validate_device(device: Device):
    if not device.configurations: raise UsbConfigError("device must contain at least one configuration")
    if device.bcd_usb_value >= 0x0300:
        if device.max_packet_size_ep0 not in (64, 512): raise UsbConfigError("USB 3.x EP0 max packet must be 64 or 512")
    elif device.bcd_usb_value >= 0x0200:
        if device.max_packet_size_ep0 != 64: raise UsbConfigError("USB 2.0 EP0 max packet must be 64")
    values = [c.configuration_value for c in device.configurations]
    if len(values) != len(set(values)): raise UsbConfigError("configuration values must be unique")
    for config in device.configurations: _validate_configuration(config)
def _validate_configuration(config):
    numbers = [i.number for i in config.interfaces]
    if len(numbers) != len(set(numbers)): raise UsbConfigError("duplicate interface numbers")
    for a in config.associations:
        expected = set(range(a.first_interface, a.first_interface + a.interface_count))
        if not expected.issubset(set(numbers)): raise UsbConfigError("IAD references missing interfaces")
    seen = set()
    for iface in config.interfaces:
        for ep in iface.endpoints:
            if ep.number == 0: raise UsbConfigError("endpoint 0 cannot be declared")
            if ep.address in seen: raise UsbConfigError(f"duplicate endpoint address 0x{ep.address:02X}")
            seen.add(ep.address)
            if ep.transfer_type == "isochronous" and ep.direction == "out": raise UsbConfigError("isochronous must be IN")
            if ep.superspeed:
                if not 0 <= ep.superspeed.max_burst <= 15: raise UsbConfigError("max_burst must be 0..15")
                if not 0 <= ep.superspeed.max_streams <= 15: raise UsbConfigError("max_streams must be 0..15")
                if not 0 <= ep.superspeed.mult <= 2: raise UsbConfigError("mult must be 0..2")
