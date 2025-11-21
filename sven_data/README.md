# sven_data

Data handling layer: dataset schemas, loaders, diff-based masking utilities, and registry for multi-source vulnerability corpora.

Contents:
- `loaders.py`: Scaffold implementations for Big-Vul / CrossVul / VUDENC datasets plus diff masking (`apply_diff_masking`) to isolate security-relevant modifications.
- `schemas.py`: Pydantic models (e.g., `GeneratedCode`) standardizing structured outputs.
- `interfaces.py`: Dataset registry & abstractions for consistent loader access.
- `__init__.py`: Public exports.

Key Concepts:
- Diff Masking: Converts vulnerable→fixed code pair into token-level mask (1 = changed region, 0 = unchanged) feeding conditional LM and KL losses.
- Registry Pattern: `DatasetRegistry.get(name)` returns loader instance enabling CLI/config-driven dataset selection.
- Placeholder Logic: Some loaders return synthetic or empty samples pending full data curation.

Extensibility:
- Implement real parsing, cleaning, and tokenization (note TODO in `loaders.py`).
- Add language-specific pre-processing (Python, Java, C++).
- Integrate caching for large corpora.

Testing:
- `tests/test_datasets.py` validates masking edge cases and registry behavior.
