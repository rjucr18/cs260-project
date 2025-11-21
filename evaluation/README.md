# evaluation

Implements model assessment metrics and interfaces for security and functional correctness.

Planned Components:
- Security Rate: Run CodeQL across generated samples to quantify vulnerability reduction.
- Pass@k: HumanEval-style functional correctness on held-out prompts.
- Interfaces (`interfaces.py`): Defines abstraction for evaluation tasks (placeholder for future expansion).

Workflow (future):
1. Generate code samples (secure & vulnerable modes).
2. Build CodeQL database and analyze for CWE detections.
3. Aggregate metrics (reductions, false positives, functional retention).

Extensibility:
- Add language-specific evaluators (Python/Java/C++).
- Integrate statistical significance testing for comparisons.
