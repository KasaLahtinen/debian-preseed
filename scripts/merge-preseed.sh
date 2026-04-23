#!/bin/bash

# Exit immediately on errors, unset variables, and pipeline failures
set -euo pipefail

VERBOSE=0
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -v|--verbose)
      VERBOSE=1
      shift
      ;;
    -*|--*)
      echo "Unknown option $1"
      echo "Usage: $0 [-v|--verbose] [INPUT_ISO_PATH] [OUTPUT_ISO_PATH]"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1")
      shift
      ;;
  esac
done

ARG1=""
ARG2=""
if [ ${#POSITIONAL_ARGS[@]} -gt 0 ]; then
    ARG1="${POSITIONAL_ARGS[0]}"
fi
if [ ${#POSITIONAL_ARGS[@]} -gt 1 ]; then
    ARG2="${POSITIONAL_ARGS[1]}"
fi

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISO_DIR="$BASE_DIR/iso"
WORK_DIR="$BASE_DIR/isofiles"
SCRIPTS_DIR="$BASE_DIR/scripts"

# Find default input ISO (first .iso that doesn't start with preseed-)
DEFAULT_ISO_IN=""
shopt -s nullglob
for iso in "$ISO_DIR"/*.iso; do
    if [[ "$(basename "$iso")" != preseed-* ]]; then
        DEFAULT_ISO_IN="$iso"
        break
    fi
done
shopt -u nullglob

# Use argument 1, or the detected ISO
ISOFILE_IN="${ARG1:-$DEFAULT_ISO_IN}"

if [ -z "$ISOFILE_IN" ]; then
    echo "Error: Could not automatically detect a base ISO in $ISO_DIR."
    echo "Please place a debian netinst iso in $ISO_DIR or specify one."
    echo "Usage: $0 [-v|--verbose] [INPUT_ISO_PATH] [OUTPUT_ISO_PATH]"
    exit 1
fi

DEFAULT_ISO_OUT="$ISO_DIR/preseed-$(basename "$ISOFILE_IN")"
ISOFILE_OUT="${ARG2:-$DEFAULT_ISO_OUT}"

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

run_quiet() {
    if [ "$VERBOSE" -eq 1 ]; then
        "$@"
    else
        "$@" >/dev/null 2>&1
    fi
}

echo "Cleaning work directory..."
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"

echo "Extracting ISO: $ISOFILE_IN"
run_quiet bsdtar -C "$WORK_DIR" -xf "$ISOFILE_IN"
chmod +w -R "$WORK_DIR"

echo "Modifying initrd..."
if [ -f "$WORK_DIR/install.amd/initrd.gz" ]; then
    gunzip "$WORK_DIR/install.amd/initrd.gz"
    # We must be in the directory containing preseed.cfg for cpio to find it
    (cd "$SCRIPTS_DIR" && {
        echo "preseed.cfg"
        if [ -f "authorized_keys" ]; then
            echo "authorized_keys"
        fi
    } | run_quiet cpio -H newc -o -A -F "$WORK_DIR/install.amd/initrd")
    gzip "$WORK_DIR/install.amd/initrd"
else
    echo "Error: initrd.gz not found at expected location."
    exit 1
fi

echo "Updating md5sums..."
cd "$WORK_DIR"
# md5sum.txt is usually part of the ISO, if it exists, update it.
if [ -f md5sum.txt ]; then
    find . -type f ! -name md5sum.txt -print0 | xargs -0 md5sum > md5sum.txt
fi

echo "Generating output ISO: $ISOFILE_OUT"
run_quiet genisoimage -r -J -b isolinux/isolinux.bin -c isolinux/boot.cat \
            -no-emul-boot -boot-load-size 4 -boot-info-table \
            -o "$ISOFILE_OUT" "$WORK_DIR"

echo "Done!"
