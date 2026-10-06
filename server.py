"""
Root launcher for the SciData Platform backend server.
Automatically ensures the correct Python 3.11 virtual environment (.venv311) is used,
even if executed from global Python 3.14 or without manually activating the venv.
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_PYTHON = ROOT / ".venv311" / "Scripts" / "python.exe"

# If invoked with another Python (e.g. global Python 3.14), re-execute under project's .venv311
if VENV_PYTHON.is_file():
    try:
        current_py = Path(sys.executable).resolve()
        target_py = VENV_PYTHON.resolve()
        if current_py != target_py:
            print(f"[SciData Launcher] Detected external Python: {sys.executable}")
            print(f"[SciData Launcher] Automatically switching to project environment: {VENV_PYTHON}")
            sys.exit(subprocess.call([str(VENV_PYTHON), str(__file__)] + sys.argv[1:]))
    except Exception as e:
        print(f"[SciData Launcher] Notice: {e}")

BACKEND_DIR = ROOT / "platform" / "backend"

# Prioritize backend directory in sys.path
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    import uvicorn

    # Default to local development configuration
    if "ENVIRONMENT" not in os.environ:
        os.environ["ENVIRONMENT"] = "development"
    if "DATABASE_URL" not in os.environ:
        os.environ["DATABASE_URL"] = "sqlite:///./platform/storage/scidata_platform.db"

    print("=" * 60)
    print("SciData Platform Backend Server")
    print(f"Python Runtime: {sys.version.split()[0]} ({sys.executable})")
    print(f"Directory:      {BACKEND_DIR}")
    print(f"Environment:    {os.environ['ENVIRONMENT']}")
    print(f"Database:       {os.environ['DATABASE_URL']}")
    print("URL:            http://127.0.0.1:8000")
    print("API Docs:       http://127.0.0.1:8000/docs")
    print("=" * 60)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(BACKEND_DIR)],
        app_dir=str(BACKEND_DIR),
    )
