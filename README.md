# debian-preseed
Debian install  preseeding

This repository should contain basic information on debian image preseeding
[Netinst ISO file](https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.4.0-amd64-netinst.iso)

Unpacking Debian installation media:
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