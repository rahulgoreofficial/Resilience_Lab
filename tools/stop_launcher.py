"""
RESILIENCE LAB - Service Termination & Process Cleanup Utility
"""

import os
import sys
import json
import socket
import signal
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
PID_FILE = ROOT_DIR / ".launcher_pids.json"


def terminate_pid(pid: int):
    """Gracefully terminates a process and its child tree."""
    if os.name == "nt":
        try:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        except Exception:
            pass
    else:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass


def free_port(port: int):
    """Kills any lingering process bound to a specific port on Windows."""
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


def main():
    print("=================================================================")
    print("             RESILIENCE LAB - PROCESS TERMINATOR                 ")
    print("=================================================================")
    print("[*] Locating active RESILIENCE LAB processes...")

    killed_any = False

    if PID_FILE.exists():
        try:
            with open(PID_FILE, "r") as f:
                pids = json.load(f)
            for key, pid in pids.items():
                if key.endswith("_pid") and isinstance(pid, int):
                    print(f"[*] Terminating {key} (PID: {pid})...")
                    terminate_pid(pid)
                    killed_any = True
            PID_FILE.unlink(missing_ok=True)
        except Exception as e:
            print(f"[-] Warning while reading PID file: {e}")

    # Fallback port check
    free_port(8000)
    free_port(5173)

    print("[+] All RESILIENCE LAB backend and frontend services have been stopped.")
    print("=================================================================")


if __name__ == "__main__":
    main()

