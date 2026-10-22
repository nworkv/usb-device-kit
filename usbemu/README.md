# usbemu

USB Raw Gadget emulator for Raspberry Pi 4.

```bash
make
sudo modprobe raw_gadget
sudo ./usbemu --def device.def --driver dwc2 --udc fe980000.usb --speed high --log usbemu.log
```

Create device.def:

```bash
python3 tools/make_device_def.py ../usbconfig/output/usb2_vendor_bulk/case.json -o device.def
```
