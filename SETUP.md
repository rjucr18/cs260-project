# SVEN Extension - Local Development Setup

This guide covers setting up the project with a Python virtual environment for local development.

## Initial Setup

### 1. Create Virtual Environment
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# If you get execution policy errors, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies
```powershell
# Make sure venv is activated (you should see (venv) in your prompt)
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install CodeQL (for security evaluation)
```powershell
# Download CodeQL CLI
# Visit: https://github.com/github/codeql-cli-binaries/releases
# Extract to a directory and add to PATH

# Verify installation
codeql --version
```

### 4. Setup Project Structure
The virtual environment will contain all Python dependencies isolated from your system Python.

Directory structure:
```
cs260 project sven/
├── venv/              # Virtual environment (gitignored)
├── data/              # Datasets (gitignored except .gitkeep)
├── checkpoints/       # Model checkpoints (gitignored except .gitkeep)
├── configs/           # Configuration files
├── prefix_tuning/     # Prefix-tuning implementation
├── models/            # Model wrappers
├── training/          # Training loops
├── evaluation/        # Evaluation scripts
└── webapp/            # Flask demo
```

## Development Workflow

### Activating the Environment
Always activate the virtual environment before working:
```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# You should see (venv) in your prompt
```

### Installing New Packages
```powershell
# Activate venv first
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### Running Training
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Run training
python train.py --config configs/python.yaml --model codegen-350m --epochs 5
```

### Running Tests
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Run pytest
pytest tests/ -v
```

### Running the Web Demo
```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Navigate to webapp
cd webapp

# Run Flask app
python app.py
```

## Deactivating the Environment
```powershell
deactivate
```

## Troubleshooting

### PowerShell Execution Policy
If you can't activate venv, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Missing GPU Support
If you don't have a GPU, you can still run on CPU (slower):
- Training will automatically use CPU if CUDA is not available
- For faster development, use the smaller codegen-350M model

### Dependencies Conflicts
If you encounter dependency conflicts:
```powershell
# Remove venv
Remove-Item -Recurse -Force venv

# Recreate
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## VS Code Integration

### Recommended Extensions
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Python Debugger (ms-python.debugpy)

### Select Python Interpreter
1. Open Command Palette (Ctrl+Shift+P)
2. Type "Python: Select Interpreter"
3. Choose `.\venv\Scripts\python.exe`

VS Code will automatically activate the venv in its integrated terminal.
