# SVEN Extension: Multi-Language Secure Code Generation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**CS260 Research Project** - Extending SVEN (Security Verification and Enhancement Network) for secure code generation across Python, Java, and C++.

## Overview

This project builds on the SVEN framework (He & Vechev, 2023) to create a practical, multi-language secure code generation system. Using prefix-tuning on CodeGen models (350M/2.7B), we guide LLMs to generate vulnerability-free code while preserving functional correctness.

### Key Features
- 🔒 **Security-Aware Generation**: Reduces common vulnerabilities (SQL injection, path traversal, buffer overflows)
- 🌐 **Multi-Language Support**: Python, Java, C++
- 🎯 **Parameter-Efficient**: Prefix-tuning requires <0.1% of model parameters
- 🐳 **Reproducible**: Dockerized training and evaluation pipeline
- 📊 **Interactive Demo**: Flask web interface for secure/vulnerable code comparison

## Quick Start

### Prerequisites
- Python 3.9+ (3.10 recommended)
- NVIDIA GPU with CUDA support (for training)
- Docker & Docker Compose (optional, for containerized workflow)

### Setup

#### Option 1: Local Development with venv (Recommended for development)
```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/sven-extension.git
cd sven-extension

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download datasets
python scripts/download_datasets.py --datasets big-vul crossvul vudenc

# Run training (small model)
python train.py --config configs/python.yaml --model codegen-350m

# Launch web demo
cd webapp
python app.py
# Access at http://localhost:5000
```

#### Option 2: Docker (Recommended for reproducibility)
```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/sven-extension.git
cd sven-extension

# Build and start containers
docker-compose up -d

# Download datasets
docker exec -it sven-dev python scripts/download_datasets.py --datasets big-vul crossvul vudenc

# Run training (small model)
docker exec -it sven-dev python train.py --config configs/python.yaml --model codegen-350m

# Launch web demo
docker-compose up webapp
# Access at http://localhost:5000
```

## Project Structure

```
.
├── prefix_tuning/     # Prefix-tuning implementation
├── models/            # CodeGen model wrappers
├── data/              # Dataset loaders (Big-Vul, CrossVul, VUDENC)
├── training/          # Three-loss training loop
├── evaluation/        # CodeQL + HumanEval metrics
├── webapp/            # Flask demo interface
├── configs/           # YAML configs per language
├── scripts/           # Utility scripts
└── checkpoints/       # Model checkpoints (gitignored)
```

## Architecture

### Three-Loss Training
1. **Conditional LM Loss**: Learn secure token probabilities
2. **Contrastive Loss**: Distinguish secure vs vulnerable code
3. **KL Divergence**: Preserve functional correctness

### Evaluation Metrics
- **Security Rate**: % vulnerability-free code (CodeQL analysis)
- **Pass@k**: Functional correctness (HumanEval benchmark)

## Development

### Branches
- `main`: Stable integration branch
- `partner1-model-engineering`: Model implementation, prefix-tuning, Docker
- `partner2-data-evaluation`: Data curation, CodeQL, HumanEval, webapp

### Collaboration Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature

# Regular commits
git add .
git commit -m "feat: implement secure prefix tuning"

# Pull request to main
git push origin feature/your-feature
```

## Performance Targets
- Security Rate: **>60% reduction** in vulnerabilities vs baseline
- Pass@k: Maintain **≥85%** of base model correctness
- Training Time: **<24 hours** on single GPU (350M model)

## Common Vulnerabilities Targeted
- **CWE-089**: SQL Injection
- **CWE-022**: Path Traversal
- **CWE-787**: Buffer Overflow

## References
- SVEN: He & Vechev (2023) - [Paper](https://arxiv.org/abs/2310.01281)
- CodeGen: Salesforce (2022) - [Model](https://github.com/salesforce/CodeGen)
- HumanEval: OpenAI (2021) - [Benchmark](https://github.com/openai/human-eval)

## Team
- **Partner 1**: Model engineering, Docker deployment
- **Partner 2**: Data curation, security evaluation, web demo

## License
MIT License - see [LICENSE](LICENSE) file for details.

---

**Note**: Replace `YOUR-USERNAME` with your actual GitHub username when pushing to remote.
