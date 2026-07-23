import importlib.metadata
import os
import platform
import tempfile
from pathlib import Path
from typing import Optional

from organizer.engine import rules as rules_module


def get_version() -> str:
    try:
        return importlib.metadata.version("file-organizer")
    except importlib.metadata.PackageNotFoundError:
        return "1.6.0"


def run_doctor(log_file: Optional[str] = "logs/organizer.log") -> int:
    print("Python File Organizer Doctor")
    print("============================")

    # 1. Version Info
    version = get_version()
    print(f"Version: {version}")

    # 2. Python Info
    py_ver = platform.python_version()
    print(f"Python: {py_ver}")

    # 3. Platform Info
    os_name = platform.system()
    os_rel = platform.release()
    print(f"OS/Platform: {os_name} {os_rel}")

    # 4. uv-managed environment detection
    is_uv = "No"
    virtual_env = os.environ.get("VIRTUAL_ENV")
    if virtual_env and ".venv" in virtual_env:
        is_uv = f"Yes (VIRTUAL_ENV={virtual_env})"
    elif Path(".venv").exists():
        is_uv = "Yes (local .venv directory found)"
    print(f"uv-managed environment: {is_uv}")

    critical_failures = []
    warnings = []

    # 5. Default rules validation
    try:
        defaults = rules_module.load_default_rules()
        if isinstance(defaults, list) and len(defaults) > 0:
            print("Default rules: OK")
        else:
            print("Default rules: FAILED (Empty rules list)")
            critical_failures.append("Default rules are empty or invalid.")
    except Exception as exc:
        print(f"Default rules: FAILED ({exc})")
        critical_failures.append(f"Could not load default rules: {exc}")

    # 6. Filesystem read validation (current directory)
    try:
        Path(".").resolve()
        os.listdir(".")
        print("Filesystem read: OK")
    except Exception as exc:
        print(f"Filesystem read: FAILED ({exc})")
        critical_failures.append(f"Cannot read current directory: {exc}")

    # 7. Filesystem write test
    temp_dir_ok = False
    try:
        # Use system temp directory or project directory
        with tempfile.TemporaryDirectory(prefix="file-organizer-test-") as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test_write.txt"
            test_file.write_text("write_test", encoding="utf-8")
            if test_file.read_text(encoding="utf-8") == "write_test":
                temp_dir_ok = True
        if temp_dir_ok:
            print("Filesystem write test: OK")
        else:
            print("Filesystem write test: FAILED (Data mismatch)")
            critical_failures.append("Temporary file write verification failed.")
    except Exception as exc:
        print(f"Filesystem write test: FAILED ({exc})")
        critical_failures.append(f"Temporary file write failed: {exc}")

    # 8. Watchdog package status
    try:
        from watchdog.observers import Observer

        if Observer is not None:
            print("Watchdog: OK")
        else:
            print("Watchdog: WARNING (Missing watchdog package observer)")
            warnings.append("watchdog package loaded, but Observer is missing.")
    except ImportError:
        print("Watchdog: WARNING (watchdog package is not installed)")
        warnings.append(
            "watchdog package is not installed. Watcher mode will not work."
        )

    # 9. Package metadata availability
    try:
        metadata = importlib.metadata.metadata("file-organizer")
        if metadata:
            print("Package metadata: OK")
        else:
            print("Package metadata: WARNING (Empty metadata)")
            warnings.append("Package metadata exists but is empty.")
    except importlib.metadata.PackageNotFoundError:
        print("Package metadata: WARNING (Package is not installed in the environment)")
        warnings.append(
            "Package metadata not found. The tool is likely running in local development mode."
        )

    # 10. Log destination check
    if log_file:
        log_path = Path(log_file)
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            # Safe write verification test by opening and closing in append mode
            with open(log_path, "a", encoding="utf-8") as f:
                # write a tiny check message to verify actual filesystem write
                f.write("")
            print(f"Log destination: OK ({log_file} is writable)")
        except Exception as exc:
            print(f"Log destination: FAILED (Cannot write to {log_file}: {exc})")
            critical_failures.append(
                f"Log destination '{log_file}' is not writable: {exc}"
            )
    else:
        print("Log destination: OK (No log file configured)")

    # Overall Status Summary
    print()
    if critical_failures:
        print("Overall status: failed")
        print("\nCritical Failures:")
        for failure in critical_failures:
            print(f" - {failure}")
        return 1
    elif warnings:
        print("Overall status: warnings")
        print("\nWarnings:")
        for warning in warnings:
            print(f" - {warning}")
        return 0
    else:
        print("Overall status: healthy")
        return 0
