"""
RESILIENCE LAB - Application Process Manager & Launcher
Project: Graph-Theoretic Critical Infrastructure Failure & Network Resilience Simulator
Author: Senior DevOps & Software Reliability Engineer
"""

import os
import sys
import time
import json
import socket
import signal
import subprocess
import webbrowser
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
LOGS_DIR = ROOT_DIR / "logs" / "application"
PID_FILE = ROOT_DIR / ".launcher_pids.json"

LOGS_DIR.mkdir(parents=True, exist_ok=True)


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Checks whether a TCP port is currently occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def free_port(port: int):
    """Frees a port by terminating lingering processes holding it."""
    if os.name == "nt":
        try:
            res = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=5)
            for line in res.stdout.strip().split("\n"):
                if f":{port} " in line and "LISTENING" in line:
                    parts = line.strip().split()
                    pid = parts[-1]
                    if pid.isdigit() and int(pid) > 0:
                        subprocess.run(["taskkill", "/F", "/PID", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        except Exception:
            pass


def wait_for_endpoint(url: str, timeout_sec: int = 25) -> bool:
    """Polls a URL until it returns HTTP 200 or times out."""
    start = time.time()
    req = Request(url, headers={"User-Agent": "ResilienceLab-Launcher"})
    while time.time() - start < timeout_sec:
        try:
            with urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    return True
        except (URLError, ConnectionError, TimeoutError, OSError):
            pass
        time.sleep(0.5)
    return False


def get_python_executable() -> str:
    """Resolves virtual environment Python or fallback system Python."""
    venv_py = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    if venv_py.exists():
        return str(venv_py)
    venv_py_unix = BACKEND_DIR / "venv" / "bin" / "python"
    if venv_py_unix.exists():
        return str(venv_py_unix)
    return sys.executable


def terminate_pid(pid: int):
    """Gracefully terminates a process and its child tree."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass


def terminate_prior_instances():
    """Terminates prior registered instances from PID file."""
    if PID_FILE.exists():
        try:
            with open(PID_FILE, "r") as f:
                pids = json.load(f)
            for key in ["backend_pid", "frontend_pid"]:
                pid = pids.get(key)
                if pid:
                    terminate_pid(pid)
            PID_FILE.unlink(missing_ok=True)
            print("[+] Prior session processes terminated cleanly.")
        except Exception as e:
            print(f"[-] Cleanup notice: {e}")


def cleanup():
    """Shuts down all spawned child processes."""
    print("\n[*] Initiating graceful shutdown of RESILIENCE LAB processes...")
    terminate_prior_instances()


def main():
    print("=================================================================")
    print("                  RESILIENCE LAB - LAUNCHER                      ")
    print("   Graph-Theoretic Critical Infrastructure Resilience Platform   ")
    print("=================================================================")

    # Check for orphaned instances and lingering ports
    if PID_FILE.exists():
        print("[!] Found existing session state. Cleaning up prior processes...")
        terminate_prior_instances()
        time.sleep(1)

    if is_port_in_use(8000):
        print("[!] Port 8000 is occupied. Terminating lingering process...")
        free_port(8000)
        time.sleep(1)

    if is_port_in_use(5173):
        print("[!] Port 5173 is occupied. Terminating lingering process...")
        free_port(5173)
        time.sleep(1)

    python_exe = get_python_executable()
    print(f"[*] Python runtime: {python_exe}")

    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR)
    db_file = (ROOT_DIR / "infrastructure_resilience.db").resolve().as_posix()
    env["DATABASE_URL"] = env.get("DATABASE_URL", f"sqlite:///{db_file}")

    # Open log handles cleanly for this session
    backend_log_file = open(LOGS_DIR / "backend.log", "a", encoding="utf-8")
    frontend_log_file = open(LOGS_DIR / "frontend.log", "a", encoding="utf-8")

    # 1. Start FastAPI Backend
    print("[*] Starting backend service (Uvicorn ASGI on port 8000)...")
    backend_cmd = [
        python_exe, "-m", "uvicorn", "app.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--log-level", "info"
    ]
    p_backend = subprocess.Popen(
        backend_cmd,
        cwd=str(BACKEND_DIR),
        env=env,
        stdout=backend_log_file,
        stderr=subprocess.STDOUT
    )

    # 2. Start Frontend Dev/Preview Server
    print("[*] Starting frontend service (Vite on port 5173)...")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    # Use dev server for live hot-reload or preview
    frontend_cmd = [npm_cmd, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"]
    p_frontend = subprocess.Popen(
        frontend_cmd,
        cwd=str(FRONTEND_DIR),
        stdout=frontend_log_file,
        stderr=subprocess.STDOUT,
        shell=(os.name == "nt")
    )

    # Save PIDs
    with open(PID_FILE, "w") as f:
        json.dump({
            "backend_pid": p_backend.pid,
            "frontend_pid": p_frontend.pid,
            "timestamp": time.time()
        }, f, indent=2)

    # 3. Wait for Backend Health
    print("[*] Awaiting backend health status at http://127.0.0.1:8000/api/v1/health...")
    if not wait_for_endpoint("http://127.0.0.1:8000/api/v1/health", timeout_sec=20):
        print("[-] Error: Backend health check timed out. Check logs/application/backend.log")
        cleanup()
        backend_log_file.close()
        frontend_log_file.close()
        sys.exit(1)
    print("[+] Backend health confirmed (200 OK).")

    # 4. Wait for Frontend
    print("[*] Awaiting frontend readiness at http://127.0.0.1:5173...")
    wait_for_endpoint("http://127.0.0.1:5173", timeout_sec=15)
    print("[+] Frontend server ready.")

    print("\n=================================================================")
    print("             RESILIENCE LAB IS READY AND OPERATIONAL!            ")
    print("=================================================================")
    print("   Application Web UI:  http://localhost:5173                   ")
    print("   REST API Base:       http://localhost:8000/api/v1            ")
    print("   Interactive Docs:    http://localhost:8000/api/v1/docs       ")
    print("   Application Logs:    logs/application/                       ")
    print("=================================================================")
    print("   Press Ctrl + C in this window to stop all services cleanly.   ")
    print("=================================================================\n")

    # Open browser automatically
    try:
        webbrowser.open("http://localhost:5173")
    except Exception:
        pass

    # Monitor child processes
    try:
        while True:
            time.sleep(1)
            if p_backend.poll() is not None:
                print(f"[-] Backend process terminated unexpectedly (exit code {p_backend.returncode}). Shutting down.")
                break
            if p_frontend.poll() is not None:
                print(f"[-] Frontend process terminated unexpectedly (exit code {p_frontend.returncode}). Shutting down.")
                break
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
        try:
            backend_log_file.close()
            frontend_log_file.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()

