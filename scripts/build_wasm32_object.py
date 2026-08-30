#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVIDES = (
    "roc_init_for_host",
    "roc_respond_for_host",
    "roc_shutdown_for_host",
    "roc_sse_advance_for_host",
    "roc_sse_drop_source_for_host",
    "roc_sse_drop_step_for_host",
)
OBJECT_NAME = "roc_app_llvm_wasm32_speed.o"
PATH_RE = re.compile(r"(/[^\s]+/" + re.escape(OBJECT_NAME) + r")")


def run(args: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=True, text=True, **kwargs)


def compile_host_o() -> Path:
    source = ROOT / "platform" / "wasm32_host.c"
    dest_dir = ROOT / "platform" / "targets" / "wasm32"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "host.o"
    zig = shutil.which("zig")
    if zig is None:
        raise SystemExit("zig is required to compile platform/wasm32_host.c")
    run(
        [zig, "cc", "-target", "wasm32-freestanding", "-c", str(source), "-o", str(dest)]
    )
    print(f"  -> {dest.relative_to(ROOT)}")
    return dest


def _copy_object_from(root: Path, dest: Path) -> bool:
    for dirpath, _, filenames in os.walk(root):
        if OBJECT_NAME in filenames:
            shutil.copy2(Path(dirpath) / OBJECT_NAME, dest)
            return True
    return False


def capture_app_object(app: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.unlink(missing_ok=True)
    roc_tmp = dest.parent / "roc-tmp"
    if roc_tmp.exists():
        shutil.rmtree(roc_tmp)
    roc_tmp.mkdir()
    env = os.environ.copy()
    env["TMPDIR"] = str(roc_tmp)
    cmd = [
        "roc",
        "build",
        "--target=wasm32",
        f"--output={dest.with_suffix('.linked.wasm')}",
        "--no-cache",
        str(app),
    ]
    found = threading.Event()

    def watch() -> None:
        while not found.is_set():
            if _copy_object_from(roc_tmp, dest):
                found.set()
                return
            time.sleep(0.002)

    watcher = threading.Thread(target=watch, daemon=True)
    watcher.start()
    proc = subprocess.Popen(
        cmd,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    copied = False
    assert proc.stdout is not None
    for line in proc.stdout:
        sys.stdout.write(line)
        match = PATH_RE.search(line)
        if match and not found.is_set():
            try:
                shutil.copy2(match.group(1), dest)
                found.set()
            except FileNotFoundError:
                pass
    code = proc.wait()
    found.wait(timeout=0.5)
    copied = dest.is_file()
    shutil.rmtree(roc_tmp, ignore_errors=True)
    if not copied or not dest.is_file():
        if code != 0:
            raise SystemExit(code)
        raise SystemExit(
            f"did not capture {OBJECT_NAME} under TMPDIR={roc_tmp}"
        )
    if code != 0:
        print(
            f"roc exited {code}; continuing because {OBJECT_NAME} was captured"
        )
    print(f"  -> {dest.relative_to(ROOT)}")


def dump_names(path: Path) -> str:
    tools = shutil.which("wasm-tools")
    if tools is None:
        raise SystemExit("wasm-tools is required to inspect wasm32 objects")
    result = run([tools, "dump", str(path)], capture_output=True)
    return result.stdout + result.stderr


def relink_exports(app_object: Path, dest: Path) -> None:
    wasm_ld = shutil.which("wasm-ld")
    if wasm_ld is None:
        raise SystemExit("wasm-ld is required to export roc_*_for_host")
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        wasm_ld,
        str(app_object),
        "-o",
        str(dest),
        "--no-entry",
        "--export-dynamic",
        "--import-undefined",
    ]
    for name in PROVIDES:
        cmd.append(f"--export={name}")
    run(cmd)
    print(f"  -> {dest.relative_to(ROOT)}")


def require_names(label: str, blob: str, names: tuple[str, ...]) -> None:
    missing = [name for name in names if name not in blob]
    if missing:
        raise SystemExit(f"{label} missing {', '.join(missing)}")
    print(f"  {label}: {', '.join(names)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the wasm32 app object and export roc_*_for_host"
    )
    parser.add_argument(
        "--app",
        type=Path,
        default=ROOT / "scripts" / "wasm32" / "hello-web.roc",
        help="0.16-shaped app that points at the local platform",
    )
    args = parser.parse_args()
    app = args.app.resolve()
    if not app.is_file():
        parser.error(f"app not found: {app}")

    out_dir = ROOT / "platform" / "targets" / "wasm32"
    app_object = out_dir / "roc_app.o"
    exported = out_dir / "hello-web.exports.wasm"

    print("Compiling stub host.o")
    compile_host_o()
    print("Capturing roc_app_llvm_wasm32_speed.o")
    capture_app_object(app, app_object)
    require_names("app object symbols", dump_names(app_object), PROVIDES)
    print("Relinking with --export of roc_*_for_host")
    relink_exports(app_object, exported)
    printed = run(
        [shutil.which("wasm-tools") or "wasm-tools", "print", str(exported)],
        capture_output=True,
    ).stdout
    require_names("exported wasm", printed, PROVIDES)
    print("wasm32 object ok")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from None
