#!/bin/bash

ISOFILE_IN="../iso/debian-12.4.0-amd64-netinst.iso"
ISOFILE_OUT="../iso/preseed-debian-12.4.0-amd64-netinst.iso"

# check for required binaries
required_bin=("bsdtar" "gunzip" "gzip" "genisoimage")
for bin in "${required_bin[@]}"; do
	if bin_path=$(command -v $bin); then
	  echo "Found $bin in $bin_path"
    else
      echo "$bin not found!"
      exit 1
	fi
done

# TEMPORARY
chmod +w -R ../isofiles/*
rm -rf ../isofiles/*
touch ../isofiles/README.md

bsdtar -C ../isofiles/ -xf $ISOFILE_IN

chmod +w -R ../isofiles/isolinux/
chmod +w -R ../isofiles/boot/
chmod +w -R ../isofiles/install.amd/
#cp ../seedfiles/qemu-preseed.txt ./preseed.cfg
#cp ../grub.cfg ../isofiles/boot/grub/grub.cfg
# BIOS boot seems to be using isolinux instead of grub
cp isolinux.cfg ../isofiles/isolinux/
gunzip ../isofiles/install.amd/initrd.gz
echo preseed.cfg | cpio -H newc -o -A -F ../isofiles/install.amd/initrd
gzip ../isofiles/install.amd/initrd
chmod -w -R ../isofiles/install.amd/

# not really sure about these checksums if they're needed
cd ../isofiles
chmod +w md5sum.txt
find -follow -type f ! -name md5sum.txt -print0 | xargs -0 md5sum > md5sum.txt
chmod -w md5sum.txt
cd ../scripts

genisoimage -r -J -b isolinux/isolinux.bin -c isolinux/boot.cat \
            -no-emul-boot -boot-load-size 4 -boot-info-table \
            -o $ISOFILE_OUT ../isofiles


