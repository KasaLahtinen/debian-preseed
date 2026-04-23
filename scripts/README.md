# Scripts Directory

This directory contains the core automation scripts for building the customized Debian preseed ISOs.

## `merge-preseed.sh`
A robust Bash script that:
1. Automatically discovers the latest Debian base ISO inside the `../iso/` directory.
2. Extracts the ISO contents and the `initrd`.
3. Injects `preseed.cfg` directly into the `initrd`.
4. Re-calculates `md5sums` to ensure the installer doesn't complain about corrupted media.
5. Generates a new bootable ISO image.

## `preseed.cfg`
The actual Debian Installer configuration file. This file is what gets embedded into the ISO. It controls the unattended installation process (locales, network, disk partitioning, user accounts, and package selection).

## `py-preseed/`
Contains Python utilities, primarily `parser.py`.
The parser reads preseed templates (`.txt`) and active configurations (`.cfg`) to generate structured JSON. This JSON is used by the `frontend/` React application to render a dynamic Form Designer.
