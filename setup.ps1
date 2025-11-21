# Quick start script for SVEN project (Windows PowerShell)
# Usage: .\setup.ps1

Write-Host "=== SVEN Project Setup ===" -ForegroundColor Cyan

# Check Python version
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.([0-9]+)") {
    $minor = [int]$matches[1]
    if ($minor -lt 10) {
        Write-Host "ERROR: Python 3.10+ required. Found: $pythonVersion" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✓ Python version: $pythonVersion" -ForegroundColor Green

# Create venv if not exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Yellow
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "Run tests: pytest tests/" -ForegroundColor Cyan
Write-Host "Start webapp: python webapp\app.py" -ForegroundColor Cyan
Write-Host "Run training: python train.py --config configs/python.yaml" -ForegroundColor Cyan
