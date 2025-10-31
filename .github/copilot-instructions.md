# SVEN Extension Project - AI Agent Instructions

## Project Overview
This is a CS260 research project extending SVEN (Security Verification and Enhancement Network) for secure code generation across multiple languages. The core goal is to use prefix-tuning to guide LLMs (CodeGen-350M/2.7B) to generate secure code while avoiding common vulnerabilities.

## Architecture & Components

### Core Modules
- **`prefix_tuning/`** - Prefix-tuning implementation for injecting learned security control vectors into frozen LLMs
- **`models/`** - CodeGen model wrappers (350M, 2.7B variants) with prefix integration
- **`data/`** - Dataset pipeline for Big-Vul, CrossVul, VUDENC with diff-based masking for vulnerability-fix pairs
- **`training/`** - Training loop implementing SVEN's three-loss architecture:
  1. Conditional language modeling loss (secure token probabilities)
  2. Contrastive loss (secure vs vulnerable distinction)
  3. KL divergence regularization (preserve functional correctness)
- **`evaluation/`** - Security Rate (CodeQL) and Pass@k (HumanEval) metrics
- **`webapp/`** - Flask-based demo for interactive secure/vulnerable code comparison

### Data Flow
1. Vulnerability-fix pairs → Diff-based masking → Extract modified regions
2. Prefix vectors + Frozen LLM → Controlled generation (secure/vulnerable modes)
3. Generated code → CodeQL analysis (CWE detection) + HumanEval testing

## Key Technical Decisions

### Why Prefix-Tuning?
- Parameter-efficient: Only trains small prefix vectors (~0.1% of model params)
- Preserves base model: No full fine-tuning required (resource-constrained friendly)
- Controllable: Can switch between secure/vulnerable generation modes

### Multi-Language Support
- Primary: Python (largest vulnerability dataset)
- Secondary: Java, C++ (demonstrate cross-language generalization)
- Use language-specific CodeQL queries for each target

## Development Workflows

### Local Development with venv (Recommended)
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run training
python train.py --config configs/python.yaml --model codegen-350m

# Run web demo
cd webapp && python app.py
```

### Docker-First Development (For reproducibility)
```bash
# Build reproducible training environment
docker build -t sven-training -f Dockerfile.train .

# Run training with GPU support
docker run --gpus all -v $(pwd)/data:/data -v $(pwd)/checkpoints:/checkpoints sven-training

# Launch web demo
docker-compose up webapp
```

### Dataset Preparation
```python
# Expected pattern: Clean → Verify → Mask
# 1. Remove duplicates and noise from Big-Vul/CrossVul/VUDENC
# 2. Manual verification subset (ensure accurate vulnerability labels)
# 3. Apply diff-based masking to isolate security-critical changes
```

### Evaluation Pipeline
```bash
# Security Rate: Run CodeQL on generated code
codeql database create --language=python ./db
codeql database analyze ./db --format=sarif-latest --output=results.sarif

# Pass@k: HumanEval functional correctness (k=1,10,100)
python evaluate_humaneval.py --model_checkpoint checkpoints/sven-codegen-350m
```

## Code Conventions

### Naming Patterns
- Prefix modules: `SecurePrefixTuning`, `VulnerablePrefixTuning`
- Loss functions: `conditional_lm_loss()`, `contrastive_security_loss()`, `kl_preservation_loss()`
- Datasets: `BigVulDataset`, `CrossVulDataset`, `VUDENCDataset`

### Configuration Management
- Use YAML configs for hyperparameters (learning rate, prefix length, batch size)
- Separate configs per language: `configs/python.yaml`, `configs/java.yaml`, `configs/cpp.yaml`
- Docker volumes for reproducibility: mount configs as read-only

### Security-Critical Code
When implementing vulnerability detection or generation:
- Always validate CWE mappings (CWE-089: SQL injection, CWE-022: path traversal, CWE-787: buffer overflow)
- Use defensive parsing for untrusted code inputs
- Log all generated vulnerable code with clear warnings

## Common Vulnerabilities We're Targeting
- **CWE-089**: SQL Injection (unsanitized queries)
- **CWE-022**: Path Traversal (unvalidated file paths)
- **CWE-787**: Buffer Overflow (unsafe memory operations)

## Testing Strategy
1. **Unit tests**: Prefix injection, loss computation, diff masking
2. **Integration tests**: End-to-end generation → CodeQL analysis
3. **Benchmark tests**: HumanEval Pass@k, Security Rate on held-out test set

## Collaboration Notes
- **Partner 1**: Model engineering, prefix-tuning, Docker deployment
- **Partner 2**: Data curation, CodeQL integration, HumanEval, Flask webapp
- Use GitHub PRs for code reviews, track progress in weekly milestones

## External Dependencies
- **Transformers**: Hugging Face library for CodeGen models
- **CodeQL**: Static analysis for vulnerability detection (install via `gh extension install github/gh-codeql`)
- **HumanEval**: Functional correctness benchmark (clone from OpenAI repo)

## Quick Start for New Contributors
```powershell
# Local development (Windows)
# 1. Setup virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download datasets (when available)
python scripts/download_datasets.py --datasets big-vul crossvul vudenc

# 4. Run sample training (small model for testing)
python train.py --config configs/python.yaml --model codegen-350m --epochs 5

# 5. Launch demo
cd webapp
python app.py
# Access at http://localhost:5000
```

```bash
# Docker alternative (all platforms)
# 1. Setup environment
docker-compose up -d
docker exec -it sven-dev bash

# 2. Download datasets
python scripts/download_datasets.py --datasets big-vul crossvul vudenc

# 3. Run sample training (small model for testing)
python train.py --config configs/python.yaml --model codegen-350m --epochs 5

# 4. Launch demo
docker-compose up webapp
# Access at http://localhost:5000
```

## Performance Targets (from proposal)
- Security Rate: >60% reduction in CodeQL-detected vulnerabilities vs baseline
- Pass@k: Maintain ≥85% of base model's functional correctness
- Training time: <24 hours on single GPU for 350M model

## References
- SVEN Paper: He & Vechev (2023) - Original prefix-tuning approach
- CodeGen: Salesforce (2022) - Base LLM for code generation
- HumanEval: OpenAI (2021) - Functional correctness benchmark
