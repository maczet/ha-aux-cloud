#!/usr/bin/env python3
"""
Standalone probe for the AUX Home cloud `running` hex state blob.

This talks to the AUX Home backend directly (no Home Assistant required) so the
byte layout decoded by ``api/aux_home.py:_decode_running_hex`` can be verified
against a real device.  Use it to resolve the byte mappings still marked
"estimated" in the decoder (cool/dry modes, the eco vs mode-mask bit collision,
and the LOW/SILENT fan conflict).

Credentials are read from the environment:

    export AUX_EMAIL='you@example.com'
    export AUX_PASSWORD='...'

Poll the current state of every device (append a CSV row each run):

    python scripts/probe_running_hex.py

Poll continuously every N seconds:

    python scripts/probe_running_hex.py --watch 30

Send a control command, then observe how the next state hex changes
(round-trip test for set_device_params); repeat the plain poll ~10 min later
because the server cache lags several minutes behind the device:

    python scripts/probe_running_hex.py --device <deviceId> --set ac_mode=1
    python scripts/probe_running_hex.py --device <deviceId> --set temp=200 --set ac_mark=3

`--set` keys/values use the internal param names understood by
AuxHomeAPI.set_device_params (e.g. pwr, temp[=°C×10], ac_mode, ac_mark,
ecomode, ac_vdir, ...).
"""

import argparse
import asyncio
import csv
import datetime as _dt
import importlib.util
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_API_DIR = _REPO_ROOT / "api"
_CSV_PATH = _REPO_ROOT / "scripts" / "probe_log.csv"


def _load_aux_home():
    """Import api/aux_home.py standalone (registers api/ as a package)."""
    pkg = "aux_cloud_api"
    if pkg not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            pkg,
            _API_DIR / "__init__.py",
            submodule_search_locations=[str(_API_DIR)],
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[pkg] = module
        spec.loader.exec_module(module)
    return importlib.import_module(f"{pkg}.aux_home")


aux_home = _load_aux_home()


def _fmt_bytes(running_hex: str) -> dict:
    """Return the load-bearing bytes as a readable dict for logging."""
    try:
        b = bytes.fromhex(running_hex)
    except ValueError:
        return {}
    out = {}
    for i in (6, 11, 13, 14, 15, 31):
        if i < len(b):
            out[f"b{i}"] = b[i]
            if i == 11:
                out["b11_bits"] = format(b[i], "08b")
    return out


async def _fetch_raw_devices(api) -> list[dict]:
    """GET /app/user_device?getStatus=1 and return the raw device list."""
    json_data = await api._make_request(
        method="GET",
        endpoint="app/user_device",
        params={"getStatus": "1"},
        ssl=False,
    )
    if isinstance(json_data, dict):
        inner = json_data.get("data")
        if isinstance(inner, list):
            return inner
    print(f"Unexpected user_device response: {json_data}", file=sys.stderr)
    return []


def _append_csv(rows: list[dict]):
    header = [
        "timestamp", "device_id", "running_hex",
        "b6", "b11", "b11_bits", "b13", "b14", "b15", "b31",
        "decoded",
    ]
    new_file = not _CSV_PATH.exists()
    with _CSV_PATH.open("a", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
        if new_file:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


async def _poll_once(api) -> None:
    raw_devices = await _fetch_raw_devices(api)
    if not raw_devices:
        print("No devices returned.")
        return

    ts = _dt.datetime.now().isoformat(timespec="seconds")
    csv_rows = []
    for raw in raw_devices:
        device_id = str(raw.get("deviceId") or raw.get("did") or "")
        status = raw.get("status") or {}
        running_hex = str(status.get("running") or "")
        decoded = aux_home._decode_running_hex(running_hex)
        parts = _fmt_bytes(running_hex)

        print(f"\n[{ts}] device {device_id}")
        print(f"  running: {running_hex}")
        print(f"  bytes  : {parts}")
        print(f"  decoded: {decoded}")

        csv_rows.append({
            "timestamp": ts,
            "device_id": device_id,
            "running_hex": running_hex,
            "b6": parts.get("b6"), "b11": parts.get("b11"),
            "b11_bits": parts.get("b11_bits"), "b13": parts.get("b13"),
            "b14": parts.get("b14"), "b15": parts.get("b15"), "b31": parts.get("b31"),
            "decoded": decoded,
        })

    _append_csv(csv_rows)
    print(f"\nLogged {len(csv_rows)} row(s) to {_CSV_PATH}")


def _parse_set(pairs: list[str]) -> dict:
    values = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"--set expects key=value, got: {pair}")
        key, _, val = pair.partition("=")
        values[key.strip()] = int(val) if val.strip().lstrip("-").isdigit() else val.strip()
    return values


async def _run(args) -> None:
    email = os.environ.get("AUX_EMAIL")
    password = os.environ.get("AUX_PASSWORD")
    if not email or not password:
        raise SystemExit("Set AUX_EMAIL and AUX_PASSWORD in the environment.")

    api = aux_home.AuxHomeAPI()
    await api.login(email, password)
    print(f"Logged in as {email} (user={api.userid})")

    if args.set:
        if not args.device:
            raise SystemExit("--set requires --device <deviceId>")
        values = _parse_set(args.set)
        print(f"Sending to {args.device}: {values}")
        resp = await api.set_device_params({"endpointId": args.device}, values)
        print(f"Control response: {resp}")
        print("Poll again in ~8-11 min to see the running hex reflect the change.")
        return

    await _poll_once(api)
    while args.watch:
        await asyncio.sleep(args.watch)
        await _poll_once(api)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--device", help="target device id for --set")
    parser.add_argument("--set", action="append", metavar="KEY=VALUE",
                        help="control param(s) to send, e.g. ac_mode=1 (repeatable)")
    parser.add_argument("--watch", type=int, default=0, metavar="SECONDS",
                        help="keep polling every N seconds")
    args = parser.parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
