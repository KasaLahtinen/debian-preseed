#!/usr/bin/env python3
"""
Debian Preseed ISO Creator
Ported from bash to Python for improved maintainability.
"""

import os
import shutil
import subprocess
import sys
import argparse
from pathlib import Path

def check_requirements():
    """Ensure all required system binaries are available."""
    required = ["bsdtar", "gunzip", "gzip", "genisoimage", "cpio", "md5sum"]
    missing = [bin for bin in required if shutil.which(bin) is None]
    if missing:
        print(f"Error: Missing required system binaries: {', '.join(missing)}")
        print("Please install them: sudo apt install libarchive-tools genisoimage cpio gzip")
        sys.exit(1)

def main():
    # Setup pathing relative to the script's location
    script_path = Path(__file__).resolve()
    base_dir = script_path.parent.parent
    iso_dir = base_dir / "iso"
    work_dir = base_dir / "isofiles"
    scripts_dir = base_dir / "scripts"

    parser = argparse.ArgumentParser(description="Automated Debian Preseed ISO Generator")
    parser.add_argument(
        "--input",
        help="Path to source Debian ISO",
        default=str(iso_dir / "debian-12.4.0-amd64-netinst.iso")
    )
    parser.add_argument(
        "--output",
        help="Path to save customized ISO",
        default=str(iso_dir / "preseed-debian-12.4.0-amd64-netinst.iso")
    )
    parser.add_argument(
        "--preseed",
        help="Path to the preseed.cfg file",
        default=str(scripts_dir / "preseed.cfg")
    )

    args = parser.parse_args()
    iso_in = Path(args.input)
    iso_out = Path(args.output)
    preseed_src = Path(args.preseed)

    check_requirements()

    if not iso_in.exists():
        print(f"Error: Input ISO not found at {iso_in}")
        sys.exit(1)

    # 1. Clean and Setup Work Directory
    print(f"--- Preparing working directory at {work_dir}")
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    # 2. Extract ISO
    print(f"--- Extracting {iso_in.name}...")
    subprocess.run(["bsdtar", "-C", str(work_dir), "-xf", str(iso_in)], check=True)

    # 3. Ensure write permissions for modification
    print("--- Setting write permissions...")
    for root, dirs, files in os.walk(work_dir):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        for f in files:
            os.chmod(os.path.join(root, f), 0o644)

    # 4. Modify initrd
    print("--- Injecting preseed.cfg into initrd...")
    initrd_gz = work_dir / "install.amd" / "initrd.gz"
    initrd = work_dir / "install.amd" / "initrd"

    if not initrd_gz.exists():
        print(f"Error: Could not find initrd.gz at {initrd_gz}")
        sys.exit(1)

    subprocess.run(["gunzip", str(initrd_gz)], check=True)

    # Append the preseed file using cpio
    preseed_name = preseed_src.name
    with subprocess.Popen(["cpio", "-H", "newc", "-o", "-A", "-F", str(initrd)],
                           stdin=subprocess.PIPE,
                           cwd=str(preseed_src.parent)) as proc:
        proc.communicate(input=f"{preseed_name}\n".encode())

    subprocess.run(["gzip", "-9", str(initrd)], check=True)

    # 5. Update MD5 Checksums
    print("--- Updating md5sum.txt...")
    if (work_dir / "md5sum.txt").exists():
        cmd = "find -follow -type f ! -name md5sum.txt -print0 | xargs -0 md5sum > md5sum.txt"
        subprocess.run(cmd, shell=True, cwd=str(work_dir), check=True)

    # 6. Build final ISO
    print(f"--- Building final ISO: {iso_out.name}")
    geniso_cmd = [
        "genisoimage", "-r", "-J",
        "-b", "isolinux/isolinux.bin", "-c", "isolinux/boot.cat",
        "-no-emul-boot", "-boot-load-size", "4", "-boot-info-table",
        "-o", str(iso_out), str(work_dir)
    ]
    subprocess.run(geniso_cmd, check=True)
    print(f"\nSuccess! Customized ISO ready at: {iso_out}")

if __name__ == "__main__":
    main()
