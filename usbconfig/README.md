# usbconfig

Declarative USB device descriptor configuration generator.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
usbconfig examples/usb2_vendor_bulk.json -o output/usb2_vendor_bulk
python -m pytest -q
```
