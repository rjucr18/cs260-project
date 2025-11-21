# scripts

Utility and CLI scripts supporting data download, interactive demos, integration tests, and validation.

Contents:
- `download_datasets.py`: Automates retrieval of vulnerability corpora (BigVul, CrossVul, VUDENC). Future: checksum + integrity verification.
- `generate_secure_compare.py`: Produces side-by-side secure vs vulnerable generations; saves JSON to `logs/`.
- `interactive_cli.py`: Simple REPL for manual prompt exploration across modes.
- `test_integration.py`: Lightweight smoke test ensuring model + trainer instantiate without full training.
- `validate_priorities.py`: Confirms Priority 0/1/2 implementation integrity (imports, configs, loaders, losses).

Usage Examples:
```powershell
python scripts/download_datasets.py --datasets big-vul crossvul
python scripts/interactive_cli.py
python scripts/generate_secure_compare.py --prompt "def unsafe(x): pass"
```

Add new scripts here for maintenance or experimentation—keep them stateless and documented.
