"""
RESILIENCE LAB - Portable Distribution Packager
Creates release/RESILIENCE_LAB_Portable.zip containing everything needed
to run on any Windows 10/11 system without running an installer.
"""

import os
import shutil
import zipfile
import hashlib
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "dist" / "RESILIENCE_LAB"
EXTRAS_DIR = ROOT_DIR / "packaging" / "dist_extras"
RELEASE_DIR = ROOT_DIR / "release"
PORTABLE_DIR = ROOT_DIR / "dist" / "RESILIENCE_LAB_Portable"
ZIP_PATH = RELEASE_DIR / "RESILIENCE_LAB_Portable.zip"

print("[*] Preparing portable distribution directory...")
if PORTABLE_DIR.exists():
    shutil.rmtree(PORTABLE_DIR)
PORTABLE_DIR.mkdir(parents=True, exist_ok=True)

# 1. Copy dist/RESILIENCE_LAB
for item in DIST_DIR.iterdir():
    dst = PORTABLE_DIR / item.name
    if item.is_dir():
        shutil.copytree(item, dst)
    else:
        shutil.copy2(item, dst)

# 2. Copy dist_extras
for item in EXTRAS_DIR.iterdir():
    shutil.copy2(item, PORTABLE_DIR / item.name)

# 3. Copy documentation PDFs
for pdf in ["INSTALLATION_GUIDE.pdf", "USER_MANUAL.pdf"]:
    pdf_file = RELEASE_DIR / pdf
    if pdf_file.exists():
        shutil.copy2(pdf_file, PORTABLE_DIR / pdf)

print("[*] Creating portable ZIP archive...")
if ZIP_PATH.exists():
    ZIP_PATH.unlink()

with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(PORTABLE_DIR):
        for file in files:
            full_path = Path(root) / file
            arc_name = full_path.relative_to(PORTABLE_DIR.parent)
            zf.write(full_path, arc_name)

zip_size_mb = round(ZIP_PATH.stat().st_size / (1024 * 1024), 2)
zip_hash = hashlib.sha256(ZIP_PATH.read_bytes()).hexdigest()
print(f"[+] Portable ZIP created: {ZIP_PATH} ({zip_size_mb} MB)")
print(f"    SHA256: {zip_hash}")

# Update SHA256SUMS.txt
entries = []
for p in sorted(RELEASE_DIR.iterdir()):
    if p.is_file() and p.name != "SHA256SUMS.txt":
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        entries.append(f"{h}  {p.name}")

(RELEASE_DIR / "SHA256SUMS.txt").write_text("\n".join(entries) + "\n", encoding="utf-8")
print("[+] Updated SHA256SUMS.txt with portable zip.")

