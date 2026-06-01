# python-file-organizer

A small CLI tool to organize files into categorized folders by file type.

Usage
-----

Run from the installed entry point or via module:

```bash
file-organizer /path/to/folder --dry-run --log-file logs/organizer.log
# or
python -m organizer.cli /path/to/folder --watch
```

Example `config.json`
---------------------

Place a `config.json` next to the project or pass options via CLI. Example:

```json
{
	"dry_run": false,
	"recursive": true,
	"watch": false,
	"ignore_dirs": [".git", "__pycache__", "node_modules"],
	"rules_file": "rules/default_rules.json"
}
```

See `organizer/config.py` for default values.

Development
-----------

Run tests locally:

```bash
pytest -q
```

