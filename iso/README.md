# ISO Directory

This directory is used for storing both the **source** Debian ISOs and the **generated** Preseed ISOs.

- Download a standard Debian `netinst` ISO (e.g., `debian-12.4.0-amd64-netinst.iso`) and place it here.
- When you run `scripts/merge-preseed.sh`, the script will automatically discover the base ISO in this directory.
- The script will output the customized ISO in this directory with a `preseed-` prefix (e.g., `preseed-debian-12.4.0-amd64-netinst.iso`).

*Note: All `.iso` files in this directory are ignored by Git.*
