import argparse
from .emit import generate
def main():
    p = argparse.ArgumentParser(prog="usbconfig")
    p.add_argument("input"); p.add_argument("-o", "--output", required=True)
    a = p.parse_args()
    print(f"Generated USB descriptor files in: {generate(a.input, a.output)}")
if __name__ == "__main__": main()
