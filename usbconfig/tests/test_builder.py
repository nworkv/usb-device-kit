from usbconfig.builder import build_configuration_block, build_endpoint
from usbconfig.loader import load_device

def test_configuration():
    d = load_device("examples/usb2_vendor_bulk.json")
    b = build_configuration_block(d.configurations[0], usb3=False)
    assert b[1] == 0x02 and (b[2] | (b[3] << 8)) == len(b)

def test_endpoint():
    d = load_device("examples/usb2_vendor_bulk.json")
    ep = d.configurations[0].interfaces[0].endpoints[0]
    assert build_endpoint(ep) == bytes.fromhex("07058102020000")
