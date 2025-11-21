# tests

Pytest-based test suite covering prefix modules, dataset masking logic, and webapp endpoints.

Structure:
- `test_prefix_tuning.py`: Validates configuration defaults, embedding shapes, projection logic, save/load, gradient flow, batch expansion.
- `test_datasets.py`: Checks diff masking correctness (no change / full change / partial), registry access, SQL injection example handling.
- `test_webapp.py`: Exercises Flask app endpoints (health, generate variations). Generation tests expect model availability; mock if running in minimal CI.

Conventions:
- Use small synthetic samples—no reliance on heavyweight external datasets for unit tests.
- Keep tests deterministic (set seeds where randomness exists).
- Avoid network downloads during standard test run; prefer dry-run or injected stubs unless performing integration testing.

Running:
```powershell
.\run_tests.ps1
# or
pytest tests/ -v
```

Extend by adding new files named `test_*.py` focusing on one module or concept each.
