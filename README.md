# debian-preseed
Automated Debian Installation Preseeding

This repository contains tools and configuration files to create customized Debian installation media using the `preseed` mechanism.

## Prerequisites

- `bsdtar` (from libarchive-tools)
- `genisoimage`
- `cpio`
- `gzip` / `gunzip`

## Quick Start

1. Download the Debian 12.4.0 Netinst ISO and place it in the `iso/` directory.
2. Configure `scripts/preseed.cfg` to your liking.
3. Run the automation script:
   ```bash
   cd scripts
   ./merge-preseed.sh
   ```

   **Alternative (Python Version):**
   ```bash
   cd scripts/py-preseed
   python3 main.py
   ```

4. The output ISO will be located at `iso/preseed-debian-12.4.0-amd64-netinst.iso`.

## Preseed Parser Library

Located in `scripts/py-preseed/`, this Python library parses Debian Preseed files (`.cfg`) and template files (`.txt`). It is designed to facilitate the creation of dynamic UI components and configuration validation.

### Key Features
- **UI-Ready Data**: Extracts descriptions, labels, and possible choices to build dropdown menus and forms dynamically.
- **Template Support**: Handles complex template files like `amd64-main-full.txt` which contain rich metadata.
- **JSON Schema Export**: Generates standard JSON Schemas from preseed data for frontend validation or API documentation.
- **React Integration**: Includes a sample `PreseedForm.jsx` component to render dynamic forms with dropdowns based on parsed data.

### Usage
You can run the parser as a standalone script to inspect parsed data or generate schemas:

```bash
cd scripts/py-preseed
# Parse a file and output structured JSON
python3 parser.py ../../seedfiles/example-preseed.txt

# To test the React UI:
# 1. Start a local web server
python3 server.py
# 2. Open http://localhost:8000 in your browser
```

## Manual Steps (for reference)

### Unpacking Debian installation media:
```
bsdtar -C DESTINATION -xf debian-10.2.0-amd64-netinst.iso
```
Unpacking initrd, adding preseed.cfg, and repacking initrd:
```
chmod +w -R isofiles/install.amd/
gunzip isofiles/install.386/initrd.gz
echo preseed.cfg | cpio -H newc -o -A -F isofiles/install.amd/initrd
gzip isofiles/install.amd/initrd
chmod -w -R isofiles/install.amd/
```
This preseed.cfg will only work on text based installer. By default Debian 12 on an qemu virtual machine boot up graphical installer which uses a different initrd.gz

Regenerating bootable ISO file:
```
genisoimage -r -J -b isolinux/isolinux.bin -c isolinux/boot.cat \
            -no-emul-boot -boot-load-size 4 -boot-info-table \
            -o preseed-debian-10.2.0-amd64-netinst.iso isofiles
```
This information was obtained from [Debian Wiki](https://wiki.debian.org/DebianInstaller/Preseed/EditIso)
Testing.