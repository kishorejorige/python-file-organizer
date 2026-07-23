# Python File Organizer

## Problem Solved
In modern workflows, files can quickly accumulate in generic folders (like Downloads or Desktop) without structure. Managing these files manually is tedious and time-consuming. 

**Python File Organizer** is a lightweight, high-performance command-line utility that scans any target directory and automatically sorts files into dedicated folders based on their extensions. It runs on both Windows and Linux, ensuring consistent organization behavior across developer environments.

---

## Key Features
- **Cross-Platform Compatibility:** Fully tested on Windows PowerShell and Linux bash/zsh.
- **Dry-Run Mode Preview:** Preview directory changes (exactly what files will move and where) before making any modifications.
- **Path Traversal Protection:** Implements strict containment checks (`pathlib.Path.is_relative_to`) to prevent rules from moving files outside the designated workspace root.
- **Custom Sorting Rules:** Easily extend default sorting rules via custom JSON files.
- **Debounced Folder Watcher:** Automatically monitors folders in real-time using `watchdog`, waiting for file write completion (debounce) before processing.
- **Self-Diagnostics:** Run a health check anytime via the `doctor` command to verify read/write access, default configurations, and dependency health.
- **Single-File Binary Compilation:** Packaged into a standalone executable using PyInstaller for installation-free distribution.

---

## Supported File Categories
Using custom demo rules, the utility sorts files into:
- **Documents:** `.pdf`, `.txt`, `.docx`, `.odt`, `.rtf`, `.md`
- **Images:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- **Spreadsheets:** `.xlsx`, `.xls`, `.csv`, `.ods`
- **Presentations:** `.pptx`, `.ppt`, `.odp`
- **Archives:** `.zip`, `.tar.gz`, `.rar`, `.7z`
- **Code:** `.py`, `.js`, `.sh`, `.bat`, `.ps1`
- **Other:** Any file format not explicitly covered by configuration rules maps to a generic fallback folder.

---

## Safety & Testing
- Comprehensive unit tests cover CLI parsing, rule merge configurations, path traversal prevention, dry-run safety, and Debounce watcher loops.
- Run the full test suite using:
  ```powershell
  uv run pytest -v --basetemp=pytest-tmp
  ```

---

## Simple Before-and-After Example

### Before Organization
```text
demo/organized/
  ├── invoice_sample.pdf
  ├── holiday_photo.jpg
  ├── sales_report.xlsx
  ├── meeting_notes.txt
  ├── project_archive.zip
  ├── presentation_sample.pptx
  └── example_script.py
```

### After Organization
```text
demo/organized/
  ├── Archives/
  │   └── project_archive.zip
  ├── Code/
  │   └── example_script.py
  ├── Documents/
  │   ├── invoice_sample.pdf
  │   └── meeting_notes.txt
  ├── Images/
  │   └── holiday_photo.jpg
  ├── Presentations/
  │   └── presentation_sample.pptx
  └── Spreadsheets/
      └── sales_report.xlsx
```

---

## How to Run the Windows Demo

To execute the demo safely and see the tool in action, run the following command in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/create_windows_demo.ps1
```

This script automates:
1. Re-creating a clean copy of the input files in the `demo/organized` directory.
2. Outputting the unorganized files list.
3. Running the file organizer in **dry-run** mode.
4. Running the file organizer for real to organize the files by type.
5. Printing the structured result.

---

## Instructions for Portfolio Screenshots

To showcase this project professionally on Upwork, capture these two screenshots:

### Screenshot 1: Before Organization & Dry-Run Preview
1. Open PowerShell and navigate to the project root.
2. Clear the terminal: `Clear-Host`
3. Run the demo setup script, but stop before real organization (or use the dry-run output).
4. Show the raw files in `demo/organized` directory.
5. Ensure the command line and terminal path are visible, e.g., `PS E:\dev\projects\python-file-organizer>`.
6. **IMPORTANT:** Ensure no personal information (usernames, email, private folder paths, IP addresses, etc.) is visible.

### Screenshot 2: Successful Execution & Organized folders
1. Run the full script `scripts/create_windows_demo.ps1`.
2. Expand the folders in the directory view or show the terminal output showing the recursive structure under `demo/organized/`.
3. Highlight the `Demo run completed successfully!` message.
4. **IMPORTANT:** Keep the terminal clean, with no user-identifying info.
