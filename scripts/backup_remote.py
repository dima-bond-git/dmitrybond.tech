#!/usr/bin/env python3
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run(cmd, check=True, input_bytes=None):
    proc = subprocess.run(cmd, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}\nSTDOUT:\n{proc.stdout.decode(errors='ignore')}\nSTDERR:\n{proc.stderr.decode(errors='ignore')}")
    return proc

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def ensure_bin(name: str):
    if shutil.which(name) is None:
        sys.exit(f"ERROR: '{name}' not found in PATH. Install OpenSSH client or Git for Windows (comes with ssh/scp).")

REMOTE_SCRIPT = r"""set -euo pipefail

TS="{TS}"
BACK="/tmp/dmb-backup-${{TS}}"
ARCH="${{BACK}}.tgz"

mkdir -p "$BACK"/{{files,firewall,packages,host,docker,etc}}

# 1) Весь проект /opt/dmb (целиком) + bare-репозиторий /opt/dmb.git
if [ -d /opt/dmb ]; then
  tar -C /opt -czf "$BACK/files/opt-dmb.tgz" dmb || true
fi
if [ -d /opt/dmb.git ]; then
  tar -C /opt -czf "$BACK/files/opt-dmb.git.tgz" dmb.git || true
elif [ -f /opt/dmb.git/hooks/post-receive ]; then
  cp -a /opt/dmb.git/hooks/post-receive "$BACK/etc/post-receive" || true
fi

# 2) Отдельно ключевые конфиги (как есть, для быстрого просмотра)
[ -f /opt/dmb/docker-compose.yml ] && cp -a /opt/dmb/docker-compose.yml "$BACK/etc/docker-compose.yml" || true
[ -f /opt/dmb/.env ] && cp -a /opt/dmb/.env "$BACK/etc/.env" || true
[ -f /opt/dmb/caddy/Caddyfile ] && cp -a /opt/dmb/caddy/Caddyfile "$BACK/etc/Caddyfile" || true

# 3) Docker метаданные (без данных контейнеров)
if command -v docker >/dev/null 2>&1; then
  (docker compose version || true) > "$BACK/docker/compose-version.txt" 2>&1
  (docker version || true) > "$BACK/docker/docker-version.txt" 2>&1
  (docker compose config || true) > "$BACK/docker/compose-config.yaml" 2>&1
  (docker ps -a || true) > "$BACK/docker/docker-ps.txt" 2>&1
  (docker images || true) > "$BACK/docker/docker-images.txt" 2>&1
  (docker volume ls || true) > "$BACK/docker/docker-volumes.txt" 2>&1
  (docker network ls || true) > "$BACK/docker/docker-networks.txt" 2>&1
fi

# 4) Firewall / сетевые вещи (пытаемся с sudo, если надо)
(ufw status verbose || sudo ufw status verbose || true) > "$BACK/firewall/ufw.txt" 2>&1
(iptables-save || sudo iptables-save || true) > "$BACK/firewall/iptables-save.txt" 2>&1
(nft list ruleset || sudo nft list ruleset || true) > "$BACK/firewall/nftables.txt" 2>&1
(ss -tulpn || true) > "$BACK/firewall/listen-ports.txt" 2>&1

# 5) Пакеты/репозитории
(lsb_release -a || true) > "$BACK/packages/lsb_release.txt" 2>&1
(cat /etc/os-release || true) > "$BACK/packages/os-release.txt" 2>&1
(dpkg --get-selections || true) > "$BACK/packages/dpkg-selections.txt" 2>&1
(apt-mark showmanual || true) > "$BACK/packages/apt-manual.txt" 2>&1
tar -czf "$BACK/packages/apt-sources.tgz" -C / etc/apt/sources.list etc/apt/sources.list.d 2>/dev/null || true

# 6) Хост-инфо
(hostnamectl || true) > "$BACK/host/hostnamectl.txt" 2>&1
(ip a || true) > "$BACK/host/ip.txt" 2>&1
(ip route || netstat -rn || true) > "$BACK/host/routes.txt" 2>&1
(id || true) > "$BACK/host/id.txt" 2>&1
(date -Is || true) > "$BACK/host/date.txt" 2>&1
(uname -a || true) > "$BACK/host/uname.txt" 2>&1

# 7) Архив
tar -C "$(dirname "$BACK")" -czf "$ARCH" "$(basename "$BACK")"
echo "$ARCH"
"""

def main():
    p = argparse.ArgumentParser(description="Backup remote Ubuntu VPS (/opt/dmb*, docker meta, firewall, packages) into ../_backups/")
    p.add_argument("--host", required=True, help="Remote host (IP or DNS)")
    p.add_argument("--user", default="deploy", help="SSH user (default: deploy)")
    p.add_argument("--port", default=22, type=int, help="SSH port (default: 22)")
    p.add_argument("--identity", help="Path to private key (optional)")
    p.add_argument("--keep", type=int, default=10, help="How many backups to keep (0 = keep all)")
    p.add_argument("--extract", action="store_true", help="Also extract the .tgz next to it for quick viewing")
    args = p.parse_args()

    ensure_bin("ssh")
    ensure_bin("scp")

    project_dir = Path.cwd()
    backup_root = project_dir.parent / "_backups"
    backup_root.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = backup_root / f"dmb-{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"==> Connecting to {args.user}@{args.host}:{args.port}")
    ssh_cmd = ["ssh", "-p", str(args.port), "-o", "StrictHostKeyChecking=accept-new"]
    if args.identity:
        ssh_cmd += ["-i", args.identity]
    ssh_cmd += [f"{args.user}@{args.host}", "bash", "-s", "--"]

    remote_script = REMOTE_SCRIPT.format(TS=ts).encode("utf-8")

    # run remote script and capture remote archive path
    proc = run(ssh_cmd, check=True, input_bytes=remote_script)
    remote_arch_path = proc.stdout.decode().strip().splitlines()[-1]
    if not remote_arch_path or not remote_arch_path.startswith("/"):
        raise RuntimeError(f"Unexpected remote archive path:\n{proc.stdout.decode()}")

    # scp archive to local
    local_tgz = run_dir / Path(remote_arch_path).name.replace("dmb-backup-", "snapshot-")
    print(f"==> Downloading {remote_arch_path} -> {local_tgz}")
    scp_cmd = ["scp", "-P", str(args.port), "-o", "StrictHostKeyChecking=accept-new"]
    if args.identity:
        scp_cmd += ["-i", args.identity]
    scp_cmd += [f"{args.user}@{args.host}:{remote_arch_path}", str(local_tgz)]
    run(scp_cmd)

    # try to remove remote temp (best-effort)
    cleanup_cmd = ssh_cmd[:-3] + ["bash", "-lc", f"rm -rf {remote_arch_path} {remote_arch_path[:-4]} || true"]
    run(cleanup_cmd, check=False)

    # write manifest
    manifest = run_dir / "_manifest.txt"
    manifest.write_text(
        f"remote_host: {args.host}\n"
        f"remote_user: {args.user}\n"
        f"port:        {args.port}\n"
        f"timestamp:   {ts}\n"
        f"archive:     {local_tgz.name}\n",
        encoding="utf-8",
    )

    # sha256
    print("==> Calculating SHA256…")
    digest = sha256_file(local_tgz)
    (run_dir / "_sha256.txt").write_text(f"{digest}  {local_tgz.name}\n", encoding="utf-8")
    print(f"SHA256: {digest}")

    # optional extract
    if args.extract:
        print("==> Extracting archive for quick browsing…")
        extract_dir = run_dir / "snapshot"
        extract_dir.mkdir(exist_ok=True)
        # use python tarfile to avoid OS dependency
        import tarfile
        with tarfile.open(local_tgz, "r:gz") as tf:
            tf.extractall(extract_dir)
        print(f"Extracted to: {extract_dir}")

    # rotation
    if args.keep > 0:
        print(f"==> Rotating backups (keep last {args.keep})…")
        dirs = sorted([p for p in backup_root.glob("dmb-*") if p.is_dir()], key=lambda p: p.name, reverse=True)
        for old in dirs[args.keep:]:
            try:
                shutil.rmtree(old)
                print(f"   removed {old}")
            except Exception as e:
                print(f"   failed to remove {old}: {e}")

    print(f"\n✅ Done. Backup folder:\n{run_dir}\nArchive:\n{local_tgz}")

if __name__ == "__main__":
    main()

# Простейший вариант (парольный вход)
#python scripts/backup_remote.py --host 62.169.31.134 --user deploy --port 22 --extract

# Если логинишься по ключу:
#python scripts/backup_remote.py --host 62.169.31.134 --user deploy --identity "C:\Users\<you>\.ssh\id_ed25519" --extract