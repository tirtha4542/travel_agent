import sys
import subprocess
from pathlib import Path

# Auto-detect and switch to .venv if running with global Python
project_root = Path(__file__).resolve().parent
venv_python = project_root / ".venv" / "Scripts" / "python.exe"

if venv_python.exists() and Path(sys.executable).resolve() != venv_python.resolve():
    print(f"[*] Switching to virtual environment: {venv_python}")
    try:
        sys.exit(subprocess.call([str(venv_python)] + sys.argv))
    except KeyboardInterrupt:
        sys.exit(0)

import uvicorn

if __name__ == "__main__":
    print("[*] Starting TreapMate AI server on http://127.0.0.1:8000 ...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
