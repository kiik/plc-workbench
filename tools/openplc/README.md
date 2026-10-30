# openplc

CLI for the PLC programs in [`customers/*/<machine>/plc/`](../../customers/): build, compile-check with matiec, deploy to a local
OpenPLC v3 runtime in Docker, read and write variables over Modbus, run simulation tests.
Python 3.11+, standard library only; needs Docker.

```sh
tools/openplc/openplc.py up                                   # build image (first time ~10 min), start runtime
tools/openplc/openplc.py check magazine-swivel -t hw     # compile only
tools/openplc/openplc.py deploy magazine-swivel          # build, check, upload, compile, start
tools/openplc/openplc.py status | logs | start | stop
tools/openplc/openplc.py symbols magazine-swivel
tools/openplc/openplc.py read  -p magazine-swivel StepNo MAG_CylExtended
tools/openplc/openplc.py write -p magazine-swivel PNL_Manual=0 SIM_PartsInMagazine=3
tools/openplc/openplc.py press -p magazine-swivel PNL_StartButton
tools/openplc/openplc.py watch -p magazine-swivel --seconds 10
tools/openplc/openplc.py test  magazine-swivel
tools/openplc/openplc.py down
```

`-t` picks the target (default `sim`). Without `-p`, `read`, `write`, `press` and `watch` take
addresses (`%QX1.0`, `%QW0`). `--json` prints one JSON object per command and one per line for
`watch`, for scripts and agents; an error prints `{"error": …}` and exits 1.

| Item | Value |
|---|---|
| Runtime | [`compose.yaml`](compose.yaml): OpenPLC_v3 at a pinned commit, image `openplc-v3:b5d4135` |
| Web UI | http://127.0.0.1:8080, openplc / openplc |
| Modbus TCP | 127.0.0.1:5020 |
| Address map | `%IX` discrete inputs, `%QX` coils (bit = byte × 8 + bit), `%IW` input registers, `%QW` holding registers 0…, `%MW` holding registers 1024… |

The CLI only talks to a runtime on this machine: `--url` must be a loopback address.

## Agents

Each command is one action with JSON in and out, so an MCP server can expose them as tools one to
one (`deploy`, `read`, `write`, `press`, `watch`, `test`), importing `openplc.py` rather than
shelling out. `watch --json` streams changes as JSON lines.
