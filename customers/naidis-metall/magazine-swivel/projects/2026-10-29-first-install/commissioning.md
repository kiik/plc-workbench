# Magazine and swivel station: commissioning record

Status: blank, filled in on site from 2026-11-21 ([plan](plan.md), 6.3 and 6.4).

Each check is written down when it is done: `ok`, or what was found and what was done about it,
with the role and date. A value changed on test goes into the
[spec](../../magazine-swivel.spec.md) in a commit that names the row here as its evidence.

## 1. Emergency stop

| Check | Result | By | Date |
|---|---|---|---|
| What 0S5 cuts in hardware (outputs, air), measured with the station powered and air on | | | |
| Pressed during a cycle: all coils off, the station in `S90_HomingRequired` | | | |
| Reset while still pressed does nothing; released and Reset↑ homes to `S0_Ready` | | | |

## 2. I/O check

Air off. Each input operated by hand and seen in the PLC; each lamp and coil switched from the
PLC and seen at the device. Rows are the spec's I/O list, section 4.

| Tag | Result | By |
|---|---|---|
| 0S1 | | |
| 0S2 | | |
| 0S3 | | |
| 0S4 | | |
| 0S5 | | |
| 0H1 | | |
| 0H2 | | |
| 0H3 | | |
| 0H4 | | |
| 1S1 | | |
| 1S2 | | |
| 2S1 | | |
| 3S1 | | |
| 3S2 | | |
| 1S3 | | |
| 4S1: beam received reads 1; beam blocked and receiver unplugged read 0 | | |
| 1Y1A | | |
| 2Y1A | | |
| 2Y1B | | |
| 3Y1A | | |
| 3Y1B | | |

## 3. Interlocks

Each output held off while its condition in the spec is false, tried in the step that drives it.

| Output | Result | By |
|---|---|---|
| `MAG_CylRetract` | | |
| `SWV_ToPickup` | | |

## 4. Safety rules

The [spec guide's safety and reliability rules](../../../../../docs/spec-guide.md#safety-and-reliability-rules),
checked on the machine.

| Rule | Result | By |
|---|---|---|
| 1. No motion starts by itself | | |
| 2. Buttons act on ↑ | | |
| 3. Every sensor wait has a timeout | | |
| 4. Homing ends in Home, then `S0` | | |
| 5. The two coils of a double solenoid never on together | | |
| 6. Coils-off motions cannot collide | | |
| 7. Stop ends the cycle at a safe point | | |
| 8. Emergency stop acts in hardware | | |
| 9. A broken wire reads the safe meaning | | |

## 5. Scenarios

The sim tests (`plc/tests/test_sim.py`), repeated by hand on the machine.

| Scenario | Sim test | Result | By |
|---|---|---|---|
| One cycle in manual | `test_manual_runs_one_cycle` | | |
| Start held down runs one cycle | `test_held_start_runs_one_cycle` | | |
| Auto until the magazine is empty | `test_auto_runs_until_magazine_empty` | | |
| Stop finishes the cycle | `test_stop_finishes_cycle` | | |
| Waits for the sorter, holding the part at pickup | `test_waits_for_next_ready` | | |
| Part lost during the turn | `test_part_lost_alarms` | | |
| Part not gripped | `test_part_not_gripped_times_out` | | |
| Swivel jammed | `test_swivel_jam_times_out` | | |
| Emergency stop, reset and homing | `test_emergency_stop_needs_reset_and_homing` | | |

## 6. Values set on test

Real caps, the sorter on its test program. Leave "Set to" empty where the spec's value held.

| Value | Set to | Cycles run | Spec commit |
|---|---|---|---|
| Timeout `S1_MagRetract` | | | |
| Timeout `S2_MagPushOut` | | | |
| Timeout `S3_SwvToPickup` | | | |
| Timeout `S4_VacuumOn` | | | |
| Timeout `S6_SwvToDropdown` | | | |
| Timeout `S91_HomeSwivel` | | | |
| Timeout `S92_HomeVacuumOff` | | | |
| Vacuum-off time `S7_VacuumOff`, `S92_HomeVacuumOff` | | | |

## 7. Acceptance

| Check | Result | By | Date |
|---|---|---|---|
| A full magazine in auto into the sorter's test program, no cap lost or misplaced | | | |
| Sorter's bins emptied, sorter back in production and checked | | Setter | |
| Station accepted | | Production manager | |

## 8. First-week alarm log

Every `S99_Alarm` from handover to 2026-11-30. A timeout changes only on a cause logged here.

| Date | Shift | Step | Cause | Action |
|---|---|---|---|---|
| | | | | |
