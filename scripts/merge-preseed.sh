#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISO_DIR="$BASE_DIR/iso"
WORK_DIR="$BASE_DIR/isofiles"
SCRIPTS_DIR="$BASE_DIR/scripts"

ISOFILE_IN="${1:-$ISO_DIR/debian-12.4.0-amd64-netinst.iso}"
ISOFILE_OUT="${2:-$ISO_DIR/preseed-debian-12.4.0-amd64-netinst.iso}"
PRESEED_FILE="$SCRIPTS_DIR/preseed.cfg"

# check for required binaries
required_bin=("bsdtar" "gunzip" "gzip" "genisoimage" "cpio" "md5sum")
for bin in "${required_bin[@]}"; do
    if ! command -v "$bin" >/dev/null 2>&1; then
      echo "Error: $bin not found. Please install it."
      exit 1
    fi
done

if [ ! -f "$ISOFILE_IN" ]; then
    echo "Error: Input ISO file not found: $ISOFILE_IN"
    exit 1
fi

echo "Cleaning work directory..."
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"

echo "Extracting ISO: $ISOFILE_IN"
bsdtar -C "$WORK_DIR" -xf "$ISOFILE_IN"
chmod +w -R "$WORK_DIR"

echo "Modifying initrd..."
if [ -f "$WORK_DIR/install.amd/initrd.gz" ]; then
    gunzip "$WORK_DIR/install.amd/initrd.gz"
    # We must be in the directory containing preseed.cfg for cpio to find it
    (cd "$SCRIPTS_DIR" && echo "preseed.cfg" | cpio -H newc -o -A -F "$WORK_DIR/install.amd/initrd")
    gzip "$WORK_DIR/install.amd/initrd"
else
    echo "Error: initrd.gz not found at expected location."
    exit 1
fi

echo "Updating md5sums..."
cd "$WORK_DIR"
# md5sum.txt is usually part of the ISO, if it exists, update it.
if [ -f md5sum.txt ]; then
    find -follow -type f ! -name md5sum.txt -print0 | xargs -0 md5sum > md5sum.txt
fi

echo "Generating output ISO: $ISOFILE_OUT"
genisoimage -r -J -b isolinux/isolinux.bin -c isolinux/boot.cat \
            -no-emul-boot -boot-load-size 4 -boot-info-table \
            -o "$ISOFILE_OUT" "$WORK_DIR"

echo "Done!"
