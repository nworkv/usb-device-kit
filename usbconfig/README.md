# usbconfig

Declarative USB device descriptor configuration generator.

```bash
pip install -e .
usbconfig examples/usb2_vendor_bulk.json -o output/usb2_vendor_bulk
python -m pytest -q
```
