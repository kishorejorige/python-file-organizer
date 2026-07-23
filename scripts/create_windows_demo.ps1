# PowerShell script to recreate and run the Windows demo safely
$ErrorActionPreference = "Stop"

# Locate the project directories relative to the script location
$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$DemoDir = Join-Path $ProjectRoot "demo"
$InputDir = Join-Path $DemoDir "input"
$OrganizedDir = Join-Path $DemoDir "organized"
$RulesFile = Join-Path $DemoDir "rules.json"

Write-Host "============================================="
Write-Host "Python File Organizer - Windows Demo System"
Write-Host "============================================="
Write-Host "Project Root: $ProjectRoot"
Write-Host "Demo Directory: $DemoDir"

# Step 1: Safety validation - verify rules and input folders exist
if (-not (Test-Path $InputDir)) {
    Write-Error "Demo input folder does not exist at: $InputDir"
    exit 1
}
if (-not (Test-Path $RulesFile)) {
    Write-Error "Demo rules file does not exist at: $RulesFile"
    exit 1
}

# Step 2: Clean and recreate demo/organized folder
Write-Host "Cleaning and recreating demo/organized folder..."
if (Test-Path $OrganizedDir) {
    Remove-Item -Recurse -Force $OrganizedDir
}
New-Item -ItemType Directory -Path $OrganizedDir | Out-Null

# Step 3: Copy clean input files to demo/organized
Write-Host "Copying fresh raw demo files to demo/organized..."
Copy-Item -Path "$InputDir\*" -Destination $OrganizedDir -Force

# Step 4: Print demo folder contents before organization
Write-Host ""
Write-Host "---------------------------------------------"
Write-Host "Demo Folder Contents BEFORE Organization:"
Write-Host "---------------------------------------------"
Get-ChildItem -Path $OrganizedDir | Select-Object -ExpandProperty Name

# Step 5: Run organization in dry-run mode
Write-Host ""
Write-Host "---------------------------------------------"
Write-Host "Executing CLI tool in DRY-RUN mode..."
Write-Host "---------------------------------------------"
uv run file-organizer $OrganizedDir --rules-file $RulesFile --dry-run

# Step 6: Run organization in real mode
Write-Host ""
Write-Host "---------------------------------------------"
Write-Host "Executing CLI tool in REAL mode..."
Write-Host "---------------------------------------------"
uv run file-organizer $OrganizedDir --rules-file $RulesFile

# Step 7: Print organized folder structure
Write-Host ""
Write-Host "---------------------------------------------"
Write-Host "Organized Result Structure:"
Write-Host "---------------------------------------------"

# Recursive list of all files/folders inside organized directory relative to it
Get-ChildItem -Path $OrganizedDir -Recurse | ForEach-Object {
    $RelativePath = $_.FullName.Substring($OrganizedDir.Length + 1)
    if ($_.PsIsContainer) {
        Write-Host "Folder: $RelativePath"
    } else {
        Write-Host "  File: $RelativePath"
    }
}

Write-Host ""
Write-Host "Demo run completed successfully!"
exit 0
