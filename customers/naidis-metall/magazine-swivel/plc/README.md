# magazine-swivel

PLC program for the magazine and swivel station:
[spec](../magazine-swivel.spec.md). The step table of
spec section 5 is [`src/station.st`](src/station.st).

| Target | Runs on | I/O |
|---|---|---|
| `hw` | Station PLC | [`targets/hw.st`](targets/hw.st): PNL2 on byte 0, XMA2 on byte 1 (assumed, PLC model `?`); E-stop and IR receiver addresses `?`, so the station stays in S90 and would wait in S5 |
| `sim` | OpenPLC in Docker | [`targets/sim.st`](targets/sim.st) with the plant model [`src/plant_sim.st`](src/plant_sim.st) |
| `sim-s7` | OpenPLC in Docker | As `sim`, with the S7 port's block [`s7/MagazineSwivel.scl`](s7/MagazineSwivel.scl) in place of `src/station.st` |

## Siemens S7-1200/1500

[`s7/`](s7/) holds the same step table as TIA Portal external sources:

| File | Contents |
|---|---|
| [`MagazineSwivel.scl`](s7/MagazineSwivel.scl) | FB `"MagazineSwivel"`: the logic, steps as `Int` constants |
| [`Main.scl`](s7/Main.scl) | Instance DB `"MagazineSwivel_DB"`, OB100 `"Startup"`, OB1 `"Main"` with the I/O map (as `targets/hw.st`; E-stop address `?`, so the station stays in S90) |
| [`sim_station.st`](s7/sim_station.st) | Simulation only: calls the FB in place of OB1 |

In TIA Portal: Program blocks → External source files → Add new external file, add
`MagazineSwivel.scl` then `Main.scl`, and Generate blocks from source on each, in that order.
TIA names the absolute addresses in OB1 `Tag_1`, …; rename them to the symbols in the comments
for a readable tag table. The sources are tested in simulation (`-t sim-s7`), not yet compiled in
TIA Portal.

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
tools/openplc/openplc.py test magazine-swivel -t sim-s7             # same, S7 port
```

The plant model starts at Home, so the program powers up in S0. The web UI at
http://127.0.0.1:8080 (openplc / openplc) shows the program and its Monitoring page.

Sim I/O, all over Modbus TCP on 127.0.0.1:5020:

| Address | Contents |
|---|---|
| `%QX0.x`, `%QX1.x` | Panel lamps, valve coils: as the `hw` target |
| `%QX2.1`–`%QX2.6` | Sensors, written by the plant model; bit = XMA2 terminal |
| `%QX3.0`–`%QX3.4` | Panel buttons, written by you; bit = PNL2 terminal. Stop and E-stop start released (1) |
| `%QX4.0`–`%QX4.2` | Faults: `SIM_VacuumFault` (gripper drops the part), `SIM_SwivelJam`, `SIM_SorterBlocked` (sorter never ready) |
| `%QX5.0` | `LNK_NextReady`, written by the plant model's sorter: busy 1 s after each cap; a cap dropped while busy counts as lost |
| `%QW0`–`%QW3` | `StepNo`, `SIM_PartsInMagazine` (writable, starts at 5), `SIM_PartsDelivered`, `SIM_PartsLost` |

`tools/openplc/openplc.py symbols magazine-swivel` lists every symbol and address.
