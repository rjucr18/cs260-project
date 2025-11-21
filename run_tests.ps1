# Run all tests with coverage
# Usage: .\run_tests.ps1

Write-Host "=== Running SVEN Tests ===" -ForegroundColor Cyan

# Activate venv if not already active
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

# Run pytest with coverage
Write-Host "`nRunning unit tests..." -ForegroundColor Yellow
pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[PASS] All tests passed!" -ForegroundColor Green
    Write-Host "Coverage report: htmlcov/index.html" -ForegroundColor Cyan
} else {
    Write-Host "`n[FAIL] Some tests failed" -ForegroundColor Red
    exit 1
}
