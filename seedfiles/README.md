# Seed Files Library

This directory contains examples, references, and template configurations for Debian preseeding.

- **`bookworm/amd64-main-full.txt`**: A comprehensive export of all possible `d-i` preseed keys, complete with their expected types (string, boolean, select, multiselect), default values, and rich descriptions. 

These templates are used by the Python parser (`scripts/py-preseed/parser.py`) to understand the schema of the Debian Installer and dynamically generate the React UI in the `frontend/` directory.
