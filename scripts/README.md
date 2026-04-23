# py-preseed

This is a Python-based port of the ISO modification logic. It provides better error reporting and a CLI interface for customizing the injection process.

## Usage

Run the script using Python 3. No external dependencies are required beyond the standard library.

```bash
python3 main.py --input ../../iso/debian.iso --output ../../iso/custom.iso
```

## Options

| Option | Default | Description |
| :--- | :--- | :--- |
| `--input` | `iso/debian-12.4.0-amd64-netinst.iso` | Source ISO file |
| `--output` | `iso/preseed-debian-12.4.0-amd64-netinst.iso` | Target path |
| `--preseed` | `scripts/preseed.cfg` | Preseed file to inject |
