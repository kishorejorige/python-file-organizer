# Python File Organizer

A clean, safe, and professional command-line tool designed to clean up clutter by automatically organizing files into categorized directories based on their extensions. It features an automated directory watcher, strict safety validation, deterministic collision resolution, and path-traversal prevention.

## Problem Solved

Users often download files, save documents, or capture media into a single messy directory (like `Downloads` or `Desktop`). Manually grouping these files into subfolders is tedious and error-prone.

**Python File Organizer** automates this workflow safely:
- It groups files into structured categories (e.g., `Images`, `Documents`, `Videos`, `Audio`, or custom folders).
- It handles file collisions deterministically without overwriting existing files.
- It can run continuously in the background to automatically process incoming files.

---

## Features

- ⚡ **Automated Organization**: Instantly categorizes files based on configured extension mappings.
- 🔍 **Background Watcher**: Uses `watchdog` to monitor target folders in real-time, automatically processing new or modified files.
- 🛡️ **Safety Guarantees**:
  - **Dry-Run Mode**: Preview what files will move and where, without executing any filesystem writes or creations.
  - **Collision Prevention**: Resolves naming conflicts deterministically by appending counter suffixes (e.g., `file_1.txt`, `file_2.txt`) rather than overwriting.
  - **Path Traversal Protection**: Rejects category targets that attempt directory escape (e.g., folder rules targeting `../` or containing path separators).
  - **Symlink Protection**: Automatically skips symlinks to avoid circular reference loops or moving targets outside the workspace.
  - **Isolation of Failures**: A permission error or failure on a single file will never abort the processing of other files.
- ⚙️ **Custom Configuration**: Merge global settings, custom mappings, and directories to ignore using a JSON config file.
- 📦 **Modern Tooling**: Managed with `uv` for lightning-fast setups, reproducible locking, and standard development commands.

---

## Architecture and Workflow

```
               [ User CLI / Watcher Event ]
                            │
                            ▼
              [ config.json Rules Loaded ]
                            │
                            ▼
          [ Validate Mappings (No Traversal) ]
                            │
                            ▼
           [ Organizer Engine: Scan Dir ]
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
       [ Match Extension ]         [ Skip Hidden/Symlink ]
              │
              ▼
     [ Target Categories ]
              │
              ▼
    [ Resolve Path Collisions ]
              │
              ▼
    [ Safe Atomic Move / Fallback ] ──► [ Rotating Log Entry ]
```

---

## Configuration Format

The tool uses `config.json` next to the executable (or a custom path passed via `--config`) to configure behavior.

```json
{
  "dry_run": false,
  "recursive": true,
  "watch": false,
  "ignore_dirs": [".git", "__pycache__", "node_modules"],
  "rules_file": "rules/default_rules.json"
}
```

### Custom Rules File

Rules mapped extensions to target folders. Example rule file (`custom_rules.json`):

```json
{
  "rules": [
    {
      "folder": "Photos",
      "extensions": [".jpg", ".png", ".heic"]
    },
    {
      "folder": "Code",
      "extensions": [".py", ".js", ".json", ".rs"]
    }
  ]
}
```

---

## Installation

### Prerequisites
- Python `3.12` or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or standard Python package managers.

### Installing Dependencies with uv

```bash
# Clone the repository
git clone git@github.com:kishorejorige/python-file-organizer.git
cd python-file-organizer

# Sync development environment and install dependencies
uv sync --dev
```

---

## Usage Examples

### Running the CLI directly

```bash
# Organize a directory once
uv run file-organizer /path/to/organize

# Preview changes without moving any files (Dry-Run)
uv run file-organizer /path/to/organize --dry-run

# Run as a background watcher to auto-organize new files
uv run file-organizer /path/to/organize --watch

# Use a custom configuration file and rules file
uv run file-organizer /path/to/organize --config custom_config.json --rules-file rules.json

# Display the application version
uv run file-organizer --version

# Run the diagnostic health check (doctor subcommand)
uv run file-organizer doctor
```

### CLI Reference

```
usage: file-organizer [-h] [--version] [--config CONFIG] [--dry-run]
                      [--log-file LOG_FILE] [--watch]
                      [--recursive | --no-recursive] [--rules-file RULES_FILE]
                      [--ignore-dir IGNORE_DIRS] [--verbose]
                      [path]

Organize files into folders based on file type

positional arguments:
  path                  Folder path to organize (or 'doctor' for diagnostics)

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --config CONFIG       Path to config file
  --dry-run             Preview changes without moving files
  --log-file LOG_FILE   Path to log file
  --watch               Watch folder and auto-organize
  --recursive, --no-recursive
                        Scan subfolders recursively
  --rules-file RULES_FILE
                        Path to a custom rules JSON file
  --ignore-dir IGNORE_DIRS
                        Directory name to ignore; can be used more than once
  --verbose             Show more detailed log output
```

---

## Docker Support

Python File Organizer can be run in a lightweight, containerized environment using Docker.

### Building the Image

To build the local Docker image:
```bash
docker build -t python-file-organizer:local .
```

### Running Diagnostics (Health Check)

The default container command runs the `doctor` diagnostic subcommand:
```bash
docker run --rm python-file-organizer:local
```

### Organizing Directories via Mounts

To organize directories on your host filesystem, mount them inside the container at `/data`:
```bash
docker run --rm \
  -v /path/to/host/folder:/data \
  python-file-organizer:local \
  file-organizer /data --dry-run
```

> [!WARNING]
> **Non-Root Permissions Caveat**: The container runs under a non-root system user `organizer` (UID `10001`) for security. Ensure that the directories you mount from the host allow read and write permissions for UID `10001` or are generally writable, otherwise file moves will fail due to Permission Denied errors.

---

## Developer Commands

The project uses a `Makefile` to simplify development workflows.

```bash
# Install all development dependencies (pytest, ruff, bandit, pip-audit, etc.)
make install-dev

# Run pytest suite
make test

# Run Ruff linter check
make lint

# Run Ruff format check
make format-check

# Run Bandit security scanner & pip-audit vulnerability checks
make security-scan

# Compile package sdist/wheel into dist/
make build

# Build a standalone executable binary using PyInstaller
make pyinstaller

# Build local Docker image
make docker-build

# Run doctor diagnostic check inside local Docker container
make docker-test
```

---

## Generated Files and Folders

- `logs/organizer.log`: Rotating logging output.
- `dist/`: Contains wheel, source tarball, and pyinstaller binary builds.
- `.venv/`: Local virtual environment managed by `uv`.

---

## Limitations & Traps

- **File Locks**: Under Windows or WSL, files that are currently open in other applications (like Microsoft Word or an active editor) might reject renaming or moving, causing them to be skipped until the next run.
- **Cross-Filesystem Moves**: Renames across physical disk partitions or mount points are non-atomic; the tool falls back safely to `shutil.move` in these scenarios.
- **Ignored Folders**: Large node_modules or cache folders should always be listed under `ignore_dirs` to prevent scanning bottlenecks.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

**Kishore Kumar**
Python Developer
GitHub: [https://github.com/kishorejorige]
