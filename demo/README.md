# Python File Organizer - Windows Demo

This directory contains the assets and configuration to demonstrate the file organizer in a safe, repeatable manner.

## Directory Structure

- `input/`: Contains clean, unorganized sample files (PDF, JPEG, XLSX, TXT, ZIP, PPTX, PY).
- `organized/`: The target folder where files are organized when running the demo script.
- `rules.json`: Custom configuration file mapping file extensions to the requested Upwork Project Catalog categories:
  - `Documents`
  - `Images`
  - `Spreadsheets`
  - `Presentations`
  - `Archives`
  - `Code`
- `screenshots/`: Folder reserved for saving screenshots of the demo execution.

## Running the Demo

To run the demo on Windows, open PowerShell inside the project root and run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/create_windows_demo.ps1
```

This script will:
1. Re-create a clean copy of the input files in the `demo/organized` directory.
2. Output the unorganized files list.
3. Run the file organizer in **dry-run** preview mode.
4. Run the file organizer for real to organize the files by type.
5. Print the structured result.
