# debian-preseed
Automated Debian Installation Preseeding

This repository contains tools and configuration files to create customized Debian installation media using the `preseed` mechanism. It includes automated shell scripts, a Python-based parser for configuration files, and a modern React frontend for dynamically designing your preseed configurations.

## Quick Start

1. Download a Debian Netinst ISO (e.g., Debian 12) and place it in the `iso/` directory.
2. Configure `scripts/preseed.cfg` to your liking, or use the React UI to generate a configuration.
3. Run the automation script:
   ```bash
   cd scripts
   ./merge-preseed.sh
   ```
   *(The script automatically discovers the base ISO in the `iso/` folder and builds a customized preseed ISO).*
4. The output ISO will be located in the `iso/` directory prefixed with `preseed-`.

## Project Structure

- `frontend/`: A Vite + React application providing a dynamic Preseed Form Designer.
- `backend/`: A NodeJS backend, prepared for future integration with Node-RED.
- `scripts/`: Contains the primary automation scripts.
  - `merge-preseed.sh`: Robust shell-based ISO creator.
  - `preseed.cfg`: The active configuration injected into the installer.
  - `py-preseed/parser.py`: Python tool for parsing preseed files and generating JSON schemas for the UI.
- `ansible/`: Scaffolded directory structure for post-installation infrastructure automation.
- `seedfiles/`: A library of preseed templates and example configurations (e.g., `amd64-main-full.txt`).
- `iso/`: Directory for source and customized ISO images (ignored by git).
- `isofiles/`: Temporary working directory used during ISO extraction and modification.

## The Preseed Form Designer (Frontend)

The frontend is a modern React application that consumes the JSON output from `parser.py` to automatically generate a configuration UI. 

To start the UI:
```bash
cd frontend
npm install
npm run dev
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

## Parsing Preseed Data

The `scripts/py-preseed/parser.py` library reads Debian Preseed templates and extracts descriptions, labels, types, and choices. 
```bash
cd scripts/py-preseed
# Extract template data as JSON for the React UI
python3 parser.py ../../seedfiles/bookworm/amd64-main-full.txt

# Parse the currently active configuration
python3 parser.py ../preseed.cfg --active
```