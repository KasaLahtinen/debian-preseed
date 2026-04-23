# Project Refactoring & Improvements Playbook

After reviewing the `debian-preseed` project structure and source files, I have compiled a set of recommendations based on industry best practices. This playbook is broken down into Git configuration, project structure, frontend/backend architecture, and infrastructure automation.

---

## 1. Git Configuration (`.gitignore`) ✅ **(COMPLETED)**

The `.gitignore` has been updated with several standard patterns and cleaned up to prevent hardcoding specific paths. 

**Completed Actions:**
- **Globalized Node and Python Ignores:** Ignored them globally by adding `/node_modules/`, `node_modules/`, `__pycache__/`, `*.py[cod]`, and `venv/` to `.gitignore`.
- **Wildcarded ISO Files:** Used a wildcard `iso/*.iso` so future updates to the base image don't accidentally get checked into Git.
- **Environment and IDE Files:** Added standard ignores for IDEs and environment variables: `.vscode/`, `.idea/`, `.env`, `.env.*`.
- **Ansible Artifacts:** Added `*.retry` to ignore failed Ansible playbook run artifacts.

---

## 2. Project Structure & Architecture ✅ **(COMPLETED)**

The project structure has been refactored to separate the React UI and the NodeJS backend.

**Completed Actions:**
- **Separated Frontend and Backend:** Created `frontend/` and `backend/` directories.
- **Modernized Frontend Build Process:** Scaffolded a Vite+React app. Converted the old in-browser tagged template literals (`htm`) into standard JSX components (`PreseedForm.jsx` and `PreseedLandingPage.jsx`) inside `frontend/src/`.
- **Cleaned Up Dependencies:** Deleted the 3.1MB `babel.min.js`, `index.html`, and `server.py` test cases.
- **Prepared Backend:** Moved the `server.js` and `package.json` to the `backend/` directory for the future Node-RED integration.

---

## 3. Shell Scripts & Automation ✅ **(COMPLETED)**

The script `scripts/merge-preseed.sh` has been updated to be more dynamic and robust.

**Completed Actions:**
- **Removed Hardcoded ISO Names:** The script now automatically detects the base `.iso` file inside the `iso/` directory and defaults to it. It also still accepts arguments to explicitly set the input and output ISO names.
- **Robust Error Handling:** Updated bash execution options to use `set -euo pipefail` which protects against unset variables and failed piped commands.

---

## 4. Ansible Infrastructure ✅ **(COMPLETED)**

A standard Ansible directory layout has been scaffolded.

**Completed Actions:**
- **Standardized Layout:** Created the standard Ansible directories: `ansible/playbooks/`, `ansible/roles/`, `ansible/group_vars/`, and `ansible/host_vars/` (with `.gitkeep` files so they can be tracked in Git).
- **Integration with Preseed (Pending User Decision):** The `volatile.yml` inventory remains untouched. Whenever ready, you can configure dynamic inventory or further document how newly spun-up VMs are targeted.

---

## Proposed Directory Structure

Implementing the above suggestions would result in a cleaner, modular architecture:

```text
debian-preseed/
├── .gitignore               # Updated with global wildcards
├── README.md
├── SUGGESTIONS.md           # This file
├── ansible/
│   ├── inventory/
│   ├── playbooks/           # Added
│   └── roles/               # Added
├── iso/                     # Contains base .iso files (ignored)
├── isofiles/                # Extracted build directory (ignored)
├── scripts/
│   ├── merge-preseed.sh     # Refactored for dynamic ISO names
│   ├── preseed.cfg
│   └── isolinux.cfg
├── backend/                 # Formerly py-preseed (Python logic)
│   ├── parser.py
│   ├── main.py
│   ├── pyproject.toml
│   └── (server.py / fastAPI app)
├── frontend/                # Added (React / Vite UI)
│   ├── package.json
│   ├── index.html
│   └── src/
│       ├── PreseedForm.jsx
│       └── PreseedLandingPage.jsx
└── seedfiles/
    ├── README.md
    ├── example-preseed.txt
    └── bookworm/
```
