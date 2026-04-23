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
4. The output ISO will be located at `iso/preseed-debian-12.4.0-amd64-netinst.iso`.

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