#!/usr/bin/env python3
"""Build, check, simulate and probe PLC projects on a local OpenPLC v3 runtime.

Standard library only. Every command prints text, or one JSON object with --json
(watch prints one JSON object per line), so the CLI can be wrapped by an MCP server.
Talks only to a runtime on this machine: agents never download to a PLC on a machine.
"""

import argparse
import http.cookiejar
import ipaddress
import json
import os
import re
import socket
import struct
import subprocess
import sys
import time
import tomllib
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL_DIR = Path(__file__).resolve().parent
IMAGE = "openplc-v3:b5d4135"
WEB_URL = "http://127.0.0.1:8080"
MODBUS_HOST, MODBUS_PORT = "127.0.0.1", 5020
USER, PASSWORD = "openplc", "openplc"


class CliError(Exception):
    pass


# ---------------------------------------------------------------- projects

def project_dir(name):
    """A path to a plc.toml folder or its machine folder, or a machine name under customers/."""
    for path in (Path(name), Path(name) / "plc"):
        if (path / "plc.toml").is_file():
            return path.resolve()
    found = [p for p in [*ROOT.glob(f"customers/*/{name}/plc"), TOOL_DIR / "examples" / name]
             if (p / "plc.toml").is_file()]
    if len(found) > 1:
        raise CliError(f"{name} is ambiguous: "
                       + ", ".join(str(p.relative_to(ROOT)) for p in found))
    if not found:
        raise CliError(f"no plc.toml in {name}, customers/*/{name}/plc or examples/{name}")
    return found[0].resolve()


def project_name(pdir):
    """The machine name: customers/<customer>/<machine>/plc → <machine>."""
    return pdir.parent.name if pdir.name == "plc" else pdir.name


def build(project, target):
    """Concatenate the target's sources into build/<target>.st and return its path."""
    pdir = project_dir(project)
    config = tomllib.loads((pdir / "plc.toml").read_text())
    targets = config.get("targets", {})
    if target not in targets:
        raise CliError(f"unknown target {target!r}; plc.toml has {', '.join(targets)}")
    parts = []
    for src in targets[target]["sources"]:
        parts.append(f"(* source: {src} *)\n{(pdir / src).read_text()}")
    out = pdir / "build" / f"{target}.st"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(parts))
    return out


LOCATED = re.compile(r"^\s*(\w+)\s+AT\s+(%[IQM][XW][\d.]+)\s*:\s*(\w+)", re.M)


def symbols(st_file):
    """Located variables of a built program: {name: (address, type)}."""
    return {m[1]: (m[2], m[3]) for m in LOCATED.finditer(Path(st_file).read_text())}


# ---------------------------------------------------------------- compiler check

def check(st_file):
    """Compile with the runtime's iec2c (matiec) in Docker; return (ok, output)."""
    script = ("cat > /tmp/p.st && cd /workdir/webserver && "
              "./iec2c -f -l -p -r -R -a -T /tmp /tmp/p.st")
    proc = subprocess.run(
        ["docker", "run", "--rm", "-i", "--entrypoint", "sh", IMAGE, "-c", script],
        input=Path(st_file).read_bytes(), capture_output=True)
    output = (proc.stdout + proc.stderr).decode(errors="replace").strip()
    return proc.returncode == 0, output


# ---------------------------------------------------------------- web API

class Runtime:
    """Session with the OpenPLC v3 web server."""

    def __init__(self, url=WEB_URL):
        host = urllib.parse.urlparse(url).hostname
        if host != "localhost" and not ipaddress.ip_address(host).is_loopback:
            raise CliError(f"refusing {url}: only a local simulation runtime is allowed")
        self.url = url.rstrip("/")
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.request("/login", {"username": USER, "password": PASSWORD})

    def request(self, path, form=None, files=None, timeout=30):
        data, headers = None, {}
        if files:
            boundary = "----openplc-cli"
            body = b""
            for key, (filename, content) in files.items():
                body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{key}\"; "
                         f"filename=\"{filename}\"\r\nContent-Type: application/octet-stream"
                         f"\r\n\r\n").encode() + content + b"\r\n"
            data = body + f"--{boundary}--\r\n".encode()
            headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        elif form is not None:
            data = urllib.parse.urlencode(form).encode()
        req = urllib.request.Request(self.url + path, data=data, headers=headers)
        with self.opener.open(req, timeout=timeout) as resp:
            return resp.read().decode(errors="replace")

    def status(self):
        match = re.search(r"Status: <i>(\w+)</i>", self.request("/dashboard"))
        return match[1] if match else "Unknown"

    def deploy(self, st_file, name, timeout=180):
        """Upload, compile and start a program; return the compilation log."""
        page = self.request("/upload-program",
                            files={"file": (Path(st_file).name, Path(st_file).read_bytes())})
        match = re.search(r"value='(\d+\.st)' id='prog_file'", page)
        if not match:
            raise CliError("upload failed: " + re.sub(r"<[^>]+>", " ", page)[-300:].strip())
        prog_file = match[1]
        self.request("/upload-program-action", {
            "prog_name": name, "prog_descr": f"{st_file}", "prog_file": prog_file,
            "epoch_time": str(int(time.time()))})
        self.request(f"/compile-program?file={prog_file}")
        deadline = time.time() + timeout
        while True:
            log = self.request("/compilation-logs")
            if "Compilation finished successfully!" in log:
                break
            if "Compilation finished with errors!" in log or time.time() > deadline:
                raise CliError("compilation failed:\n" + log)
            time.sleep(1)
        self.request("/start_plc")
        return log

    def start(self):
        self.request("/start_plc")

    def stop(self):
        self.request("/stop_plc")

    def logs(self):
        return self.request("/runtime_logs")


# ---------------------------------------------------------------- Modbus

def modbus_ref(address):
    """%QX1.2 -> (kind, index). OpenPLC v3 maps %IX/%QX bits to discrete inputs/coils,
    %IW to input registers, %QW to holding registers 0.., %MW to holding registers 1024.."""
    m = re.fullmatch(r"%([IQM])([XW])(\d+)(?:\.(\d))?", address)
    if not m:
        raise CliError(f"unsupported address {address}")
    area, size, num, bit = m[1], m[2], int(m[3]), m[4]
    if size == "X":
        if area == "M" or bit is None:
            raise CliError(f"unsupported address {address}")
        return ("di" if area == "I" else "coil"), num * 8 + int(bit)
    return {"I": "ir", "Q": "hr", "M": "hr"}[area], num + (1024 if area == "M" else 0)


class Modbus:
    """Minimal Modbus TCP client: function codes 1-6."""

    READ_FC = {"coil": 1, "di": 2, "hr": 3, "ir": 4}

    def __init__(self, host=MODBUS_HOST, port=MODBUS_PORT):
        self.sock = socket.create_connection((host, port), timeout=3)
        self.tid = 0

    def close(self):
        self.sock.close()

    def _call(self, fc, payload):
        self.tid = (self.tid + 1) & 0xFFFF
        self.sock.sendall(struct.pack(">HHHBB", self.tid, 0, len(payload) + 2, 1, fc) + payload)
        header = self._recv(7)
        _, _, length, _ = struct.unpack(">HHHB", header)
        body = self._recv(length - 1)
        if body[0] & 0x80:
            raise CliError(f"modbus exception {body[1]} for function {fc}")
        return body[1:]

    def _recv(self, n):
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                raise CliError("modbus connection closed")
            data += chunk
        return data

    def read(self, kind, start, count):
        body = self._call(self.READ_FC[kind], struct.pack(">HH", start, count))
        data = body[1:]
        if kind in ("coil", "di"):
            return [bool(data[i // 8] >> (i % 8) & 1) for i in range(count)]
        return [struct.unpack(">h", data[2 * i:2 * i + 2])[0] for i in range(count)]

    def write(self, kind, index, value):
        if kind == "coil":
            self._call(5, struct.pack(">HH", index, 0xFF00 if value else 0))
        elif kind == "hr":
            self._call(6, struct.pack(">Hh", index, int(value)))
        else:
            raise CliError("only coils (%QX) and holding registers (%QW, %MW) are writable")


class Io:
    """Read and write a program's variables by symbol or address over Modbus."""

    def __init__(self, st_file=None):
        self.symbols = symbols(st_file) if st_file else {}
        self.modbus = Modbus()

    def resolve(self, name):
        address = self.symbols[name][0] if name in self.symbols else name
        if not address.startswith("%"):
            raise CliError(f"unknown symbol {name}")
        return modbus_ref(address)

    def read(self, names):
        refs = {name: self.resolve(name) for name in names}
        values = {}
        for kind in {k for k, _ in refs.values()}:
            idx = [i for k, i in refs.values() if k == kind]
            lo = min(idx)
            block = self.modbus.read(kind, lo, max(idx) - lo + 1)
            for name, (k, i) in refs.items():
                if k == kind:
                    values[name] = block[i - lo]
        return {name: values[name] for name in names}

    def write(self, name, value):
        kind, index = self.resolve(name)
        self.modbus.write(kind, index, value)

    def press(self, name, ms=200):
        self.write(name, 1)
        time.sleep(ms / 1000)
        self.write(name, 0)


def parse_value(text):
    lowered = text.lower()
    if lowered in ("true", "on"):
        return 1
    if lowered in ("false", "off"):
        return 0
    return int(text)


# ---------------------------------------------------------------- commands

def compose(*args):
    return subprocess.run(["docker", "compose", "-f", str(TOOL_DIR / "compose.yaml"), *args],
                          capture_output=True, text=True)


def cmd_build(a):
    out = build(a.project, a.target)
    return {"file": str(out)}, str(out)


def cmd_check(a):
    out = build(a.project, a.target)
    ok, output = check(out)
    result = {"file": str(out), "ok": ok, "output": output}
    if not ok:
        raise CliError(output or "iec2c failed")
    return result, f"ok: {out}"


def cmd_up(a):
    proc = compose("up", "-d", "--wait")
    if proc.returncode:
        raise CliError(proc.stderr)
    return {"url": WEB_URL, "modbus": f"{MODBUS_HOST}:{MODBUS_PORT}"}, \
        f"runtime up: {WEB_URL} (openplc/openplc), Modbus {MODBUS_HOST}:{MODBUS_PORT}"


def cmd_down(a):
    proc = compose("down")
    if proc.returncode:
        raise CliError(proc.stderr)
    return {"ok": True}, "runtime down"


def cmd_deploy(a):
    out = build(a.project, a.target)
    ok, output = check(out)
    if not ok:
        raise CliError(output)
    runtime = Runtime(a.url)
    runtime.deploy(out, f"{project_name(project_dir(a.project))} ({a.target})")
    time.sleep(1)
    status = runtime.status()
    return {"file": str(out), "status": status}, f"deployed {out}: {status}"


def cmd_status(a):
    status = Runtime(a.url).status()
    return {"status": status}, status


def cmd_start(a):
    runtime = Runtime(a.url)
    runtime.start()
    status = runtime.status()
    return {"status": status}, status


def cmd_stop(a):
    runtime = Runtime(a.url)
    runtime.stop()
    status = runtime.status()
    return {"status": status}, status


def cmd_logs(a):
    log = Runtime(a.url).logs()
    return {"log": log}, log


def io_for(a):
    return Io(build(a.project, a.target) if a.project else None)


def cmd_symbols(a):
    table = symbols(build(a.project, a.target))
    result = {name: {"address": addr, "type": typ} for name, (addr, typ) in table.items()}
    return result, "\n".join(f"{n:24} {addr:8} {typ}" for n, (addr, typ) in table.items())


def cmd_read(a):
    io = io_for(a)
    names = a.names or list(io.symbols)
    values = io.read(names)
    return values, "\n".join(f"{n:24} {int(v)}" for n, v in values.items())


def cmd_write(a):
    io = io_for(a)
    written = {}
    for item in a.assignments:
        name, _, value = item.partition("=")
        io.write(name, parse_value(value))
        written[name] = parse_value(value)
    return written, " ".join(f"{n}={v}" for n, v in written.items())


def cmd_press(a):
    io_for(a).press(a.name, a.ms)
    return {"pressed": a.name, "ms": a.ms}, f"pressed {a.name} for {a.ms} ms"


def cmd_watch(a):
    io = io_for(a)
    names = a.names or list(io.symbols)
    last = None
    end = time.time() + a.seconds if a.seconds else None
    while end is None or time.time() < end:
        values = io.read(names)
        if values != last:
            changed = {n: v for n, v in values.items() if last is None or last[n] != v}
            line = {"t": round(time.time(), 3), **changed}
            print(json.dumps(line) if a.json else
                  " ".join(f"{n}={int(v)}" for n, v in changed.items()), flush=True)
            last = values
        time.sleep(a.interval)
    return None, None


def cmd_test(a):
    pdir = project_dir(a.project)
    if not a.no_deploy:
        cmd_deploy(a)
    proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-v",
                           "-s", str(pdir / "tests")],
                          capture_output=True, text=True, env={
                              **os.environ,
                              "PYTHONPATH": str(TOOL_DIR), "OPENPLC_PROJECT": str(pdir),
                              "OPENPLC_TARGET": a.target})
    if proc.returncode:
        raise CliError(proc.stderr)
    return {"ok": True, "output": proc.stderr}, proc.stderr


def main(argv=None):
    parser = argparse.ArgumentParser(prog="openplc", description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--url", default=WEB_URL, help="local runtime web URL")
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name, func, help, project=None):
        p = sub.add_parser(name, help=help)
        if project == "required":
            p.add_argument("project", help="machine name under customers/, or a path with plc.toml")
        elif project == "optional":
            p.add_argument("-p", "--project", help="resolve symbols from this project")
        if project:
            p.add_argument("-t", "--target", default="sim")
        p.set_defaults(func=func)
        return p

    add("build", cmd_build, "write build/<target>.st", "required")
    add("check", cmd_check, "compile with iec2c (matiec) in Docker", "required")
    add("up", cmd_up, "start the local runtime container")
    add("down", cmd_down, "stop the local runtime container")
    add("deploy", cmd_deploy, "check, upload, compile and start on the local runtime", "required")
    add("status", cmd_status, "runtime status")
    add("start", cmd_start, "start the PLC program")
    add("stop", cmd_stop, "stop the PLC program")
    add("logs", cmd_logs, "runtime log")
    add("symbols", cmd_symbols, "list located variables", "required")
    add("read", cmd_read, "read variables over Modbus", "optional") \
        .add_argument("names", nargs="*", help="symbols or addresses; default all")
    add("write", cmd_write, "write variables over Modbus", "optional") \
        .add_argument("assignments", nargs="+", metavar="NAME=VALUE")
    p = add("press", cmd_press, "pulse a coil to 1, as a button press", "optional")
    p.add_argument("name")
    p.add_argument("--ms", type=int, default=200)
    p = add("watch", cmd_watch, "print variables when they change", "optional")
    p.add_argument("names", nargs="*")
    p.add_argument("--interval", type=float, default=0.05)
    p.add_argument("--seconds", type=float, help="stop after this long")
    add("test", cmd_test, "deploy, then run the project's tests/", "required") \
        .add_argument("--no-deploy", action="store_true")

    a = parser.parse_args(argv)
    try:
        result, text = a.func(a)
    except (CliError, OSError) as e:
        print(json.dumps({"error": str(e)}) if a.json else f"error: {e}", file=sys.stderr)
        return 1
    if text is not None:
        print(json.dumps(result) if a.json else text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
