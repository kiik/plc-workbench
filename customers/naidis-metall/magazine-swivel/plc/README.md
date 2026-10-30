# magazine-swivel

PLC program for the magazine and swivel station:
[spec](../spec.md). The step table of
spec section 5 is [`src/station.st`](src/station.st).

| Target | Runs on | I/O |
|---|---|---|
| `hw` | Station PLC | [`targets/hw.st`](targets/hw.st): PNL2 on byte 0, XMA2 on byte 1 (assumed, PLC model `?`); E-stop address `?`, so the station stays in S90 |
| `sim` | OpenPLC in Docker | [`targets/sim.st`](targets/sim.st) with the plant model [`src/plant_sim.st`](src/plant_sim.st) |

## Simulating

```sh
tools/openplc/openplc.py up
tools/openplc/openplc.py deploy magazine-swivel          # sim target
tools/openplc/openplc.py watch -p magazine-swivel StepNo SWV_AtPickup SIM_PartsDelivered &
tools/openplc/openplc.py press -p magazine-swivel PNL_StartButton   # one cycle (manual)
tools/openplc/openplc.py write -p magazine-swivel PNL_EStopOk=0     # → S90
tools/openplc/openplc.py write -p magazine-swivel PNL_EStopOk=1
tools/openplc/openplc.py press -p magazine-swivel PNL_ResetButton   # S90 → homing → S0
tools/openplc/openplc.py write -p magazine-swivel PNL_Manual=0      # auto
tools/openplc/openplc.py test magazine-swivel                       # scenario tests
```

The plant model starts at Home, so the program powers up in S0. The web UI at
http://127.0.0.1:8080 (openplc / openplc) shows the program and its Monitoring page.

Sim I/O, all over Modbus TCP on 127.0.0.1:5020:

| Address | Contents |
|---|---|
| `%QX0.x`, `%QX1.x` | Panel lamps, valve coils: as the `hw` target |
| `%QX2.1`–`%QX2.6` | Sensors, written by the plant model; bit = XMA2 terminal |
| `%QX3.0`–`%QX3.4` | Panel buttons, written by you; bit = PNL2 terminal. Stop and E-stop start released (1) |
| `%QX4.0`, `%QX4.1` | Faults: `SIM_VacuumFault` (gripper drops the part), `SIM_SwivelJam` |
| `%QW0`–`%QW3` | `StepNo`, `SIM_PartsInMagazine` (writable, starts at 5), `SIM_PartsDelivered`, `SIM_PartsLost` |

`tools/openplc/openplc.py symbols magazine-swivel` lists every symbol and address.
