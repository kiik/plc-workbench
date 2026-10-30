# Spec guide

How to write a machine spec: one Markdown file per machine, `customers/<customer>/<machine>/spec.md`;
a machine is what one PLC controls, and one with several stations has one `<station>.md` per
station instead. The spec is kept current for as long as the machine runs. Drawings, labels and
notes it is taken from go in `sources/` next to it. The program that implements it is `plc/`
([PLC guide](plc-guide.md)); each project on the machine has its plan in
`projects/<YYYY-MM-DD>-<project>/` ([plan guide](plan-guide.md)).
Example: [`magazine-swivel`](../customers/naidis-metall/magazine-swivel/spec.md).
Scope: digital I/O and one step sequence per station.

## Rules

1. Never invent an address or connection. Take tags from labels or drawings; where there are none,
   assign them by the tag rules. Unknowns and conflicts become open questions; quote the original
   wording.
2. Each fact lives in one place; no tables derived from other tables.
3. Change a value only on evidence (label, drawing, measurement, test). Specs are kept in git; the
   commit message names the evidence.
4. Agents do not download to PLCs, force outputs, set `virtual` signals on a running machine or
   switch power.
5. The spec holds the specification only; no rationale or history, except the Prevents column of
   the interlocks. Apply an answered question, then delete it; the commit message quotes the
   question and the answer.

## Spec sections

Each section uses only names defined in the sections above it.

| # | Section | Contents |
|---|---|---|
| 1 | Modules | Prefix, name, local name, tag groups |
| 2 | Components | Hardware not in Pneumatics or the I/O list (PLC, I/O devices, air supply, gauges): tag, name, local name; for I/O devices the I/O count, which side terminals are labeled from, PLC connection |
| 3 | Pneumatics | One row per actuator: actuator tag, name, valve tag, valve type, coils, what the actuator does with its coils off |
| 4 | I/O list | One row per signal |
| 5 | Control | Rules for every step, interlocks, step table |
| 6 | Open questions | `- [ ] **?n** …` |

Title: `# <Station name> (<local name>)`, then a status line: `Status: draft`,
`Status: reviewed <date> <name>` or `Status: commissioned <date> <name>`. A spec with open
questions or a `?` is a draft.

## Naming

| Item | Rule | Example |
|---|---|---|
| Module | Three letters, one per mechanical unit, from [Modules](#modules); symbol prefix | `MAG`, `GRP` |
| Group | Number of an actuator chain; each group belongs to one module, listed in section 1 | `0`, `3` |
| Tag | `<group><class><index>[coil]` as labeled; see [Tags](#tags) | `3Y1A` |
| Device | As labeled on the equipment or drawing; `?` if unlabeled | `PNL2`, `XMA2` |
| Address | `<DEVICE>.<terminal>`, terminal exactly as labeled on the device. `?` = unknown; `virtual` = PLC tag with no terminal yet, set from simulation or an HMI | `XMA2.I4`, `PNL2.O0`, `virtual` |
| Symbol | `<MOD>_<PascalCase>`, where `MOD` is the module of the tag's group; unique per PLC, ≤ 24 characters. Inputs name the state that reads 1, outputs the action | `MAG_CylExtended`, `PNL_StopReleased` (NC), `MAG_CylRetract` |
| Step | `S<n>_<PascalCase>`: `S0` ready, `S1`… cycle, `S90` homing required, `S91`… homing, `S99` alarm | `S3_SwvToPickup` |
| Internal | `PascalCase`, no module prefix | `StopReq` |
| Question | `?n`, numbered per spec, never reused (check git history); panel labels are quoted as written | `?3`, lamp `Q1` |

### Modules

| Module | Unit |
|---|---|
| `PNL` | Control panel |
| `MAG` | Magazine |
| `SWV` | Swivel |
| `GRP` | Gripper |
| `CNV` | Conveyor |
| `LFT` | Lift |
| `PRS` | Press |
| `SRT` | Sorter |

Use these codes; add a new three-letter code here before using it in a spec. A second unit of the
same kind in one station replaces the last letter with a digit: `CNV`, `CN2`.

### Tags

| Part | Meaning |
|---|---|
| group | Actuator chain; an actuator, its valve, coils and sensors share it. A module may own several groups. `0` = control panel and shared hardware |
| class | Kind of component, from the table below |
| index | Number within group and class, from 1 |
| coil | `A` for the first coil, `B` for the second coil of a double solenoid |

| Class | Kind | Examples | PLC side |
|---|---|---|---|
| `S` | Switch or sensor | Push button, key switch, emergency stop, cylinder position switch, inductive or optical sensor, light barrier, pressure switch | input |
| `Y` | Solenoid | Valve coil, brake, lock | output |
| `H` | Signalling device | Lamp, beacon, buzzer | output |
| `K` | Relay, contactor | Motor contactor, interposing relay | output |
| `M` | Electric motor | Conveyor motor | output |
| `A` | Pneumatic actuator | Cylinder, swivel, gripper, vacuum generator | — |
| `V` | Valve | 5/2 valve body (its coils are `Y`), valve island | — |
| `Z` | Air supply | Service unit, regulator, shut-off valve | — |
| `P` | Measuring instrument | Pressure gauge | — |
| `X` | Terminal, connector | Terminal block, I/O connector | — |
| `F` | Protective device | Fuse, circuit breaker | — |
| `G` | Power supply | 24 V DC supply | — |

Classes with a PLC side appear in the I/O list, `A` and `V` in Pneumatics, the others in Components.
Assigning tags where the equipment has none: pick the group and class, number in channel order,
and mark the tag on the equipment. Where labels or drawings use another tag scheme, keep their tags
and ask in an open question which group each belongs to.

### Abbreviations

| Term | Meaning |
|---|---|
| PLC | Programmable logic controller |
| `I` / `O` | Input / output terminal, as labeled on the device |
| NO / NC | Normally open / normally closed contact |
| 5/2 | Valve with 5 ports and 2 positions |
| 5/3 closed centre | Valve with 5 ports and 3 positions; with both coils off the ports close and the cylinder stops |
| Home | Rest position, defined per spec; required before Ready |
| Timeout | Longest time a step may wait for its sensor before `S99_Alarm` |
| `↑` | Pressed in this scan (rising edge) |

## Making the I/O list

| Tag | Address | Direction | Symbol | Description |
|---|---|---|---|---|
| 1S1 | XMA2.I1 | input | `MAG_CylExtended` | Magazine cylinder: 1 = extended |

1. Take tags and addresses from labels, drawings or notes.
2. Write the address as the device labels it. Some devices label from their own side (a panel's
   buttons on `O`, its lamps on `I`); say so in Components. Direction is the PLC side, `input` or
   `output`, from the tag class; on such a device it is the opposite of the terminal letter.
3. The description becomes the PLC tag comment: `<unit or device>: 1 = <meaning>`, adding
   `0 = …` where it is not just the opposite. Contacts are NO; write NC in the description.
4. Unknown address: `?`, and an open question naming the tag. A planned signal with no terminal
   yet: `virtual`, with its default value in the description and an open question. Safety signals
   (emergency stop, guard switches) are never `virtual`.
5. Order: by device, PLC inputs before outputs, then by channel; `?` and `virtual` last in their group.
6. Review before wiring:
   - tags, addresses and symbols are unique; symbols also across all specs on the same PLC;
   - every channel exists on its device;
   - Direction matches the tag class, and fits the address given which side the device labels
     from;
   - the symbol prefix is the module of the tag's group;
   - every symbol in the control section is in the I/O list.

## Control

Section 5 of a spec has three parts:

1. Rules that apply in every step: the Home condition, power-up, emergency stop, Stop, auto and manual.
2. Interlocks: `| Output | Only while | Prevents |`. An interlock holds in every step, so an output
   can never drive into a collision. Prevents names the collision in a few words.
3. Step table: `| Step | Outputs on | Next when | Timeout → S99 |`. Outputs not listed are off. An
   output may carry a modifier that applies to it alone: `(blink)` is 1 Hz, `(if <condition>)` is
   on only while the condition holds, `(blink if <condition>)` is both. "Next when" lists every
   exit in priority order; the timeout is checked last. `↑` means pressed in this scan. Rows go
   in run order: homing, ready, cycle, alarm.

Wait for a sensor where there is one. A wait with no sensor (vacuum building up, a part settling) is
a step of its own with a time as its exit, `300 ms → S5`; the time is changed on test. Valve
switching times, cylinder speeds and input filters are not in the spec.

### Implementing

Implement the table the same way on every PLC. Rows become `CASE` branches, the "Outputs on"
column becomes one line per output, and interlocks are ANDed onto that line. The example is
IEC 61131-3 Structured Text (CODESYS, TwinCAT, Siemens SCL, Rockwell ST); in ladder each output
line is one rung. `CurStep` is an enumeration (not `Step`: `STEP` is an IEC keyword); where the
PLC has none (Rockwell), use integer constants named like the steps. `FirstScan` is 1 in the first
scan only (Rockwell `S:FS`; on Siemens set it in OB100; on CODESYS, TwinCAT and OpenPLC a variable
initialised to 1 and cleared at the end of the scan). Every `END_IF` and `END_CASE` ends with `;`.

```iecst
StepTimer(IN := CurStep = LastStep, PT := T#24H);  (* TON; restarts on every step change *)
StepTime := StepTimer.ET;
LastStep := CurStep;

StartTrig(CLK := PNL_StartButton);      (* one R_TRIG instance per button *)
StartP := StartTrig.Q;                  (* 1 for one scan on 0 → 1; a button held at power-up
                                           gives 1 in the first scan only, which FirstScan skips *)

IF FirstScan THEN
    IF Home THEN CurStep := S0_Ready; ELSE CurStep := S90_HomingRequired; END_IF;
ELSIF NOT PNL_EStopOk THEN
    CurStep := S90_HomingRequired;
ELSE
    CASE CurStep OF                          (* one branch per row; at most one transition per scan *)
    S1_MagRetract:
        IF MAG_CylRetracted THEN CurStep := S2_MagPushOut;
        ELSIF StepTime >= T#3S THEN CurStep := S99_Alarm; END_IF;
    END_CASE;
END_IF;

(* one line per output; never assigned anywhere else *)
MAG_CylRetract := CurStep = S1_MagRetract AND SWV_AtDropdown;
PNL_StartLamp := CurStep = S0_Ready AND Blink1Hz OR CurStep = S1_MagRetract;
```

`Blink1Hz` is 0.5 s on, 0.5 s off.

### Safety and reliability rules

Check each one against the table in review:

1. No motion starts by itself: after power-up, an alarm or an emergency stop, motion needs an
   operator pressing Start or Reset. The only exception is a coils-off motion from Pneumatics
   (a spring return), which rule 6 checks.
2. Buttons act on `↑`; a button held at power-up does nothing.
3. Every sensor wait has a timeout to `S99`. `S90` and `S99` are left only by Reset↑, into homing.
4. Homing ends in Home, then `S0`; `S0` goes to `S90` if Home is lost.
5. The two coils of a double solenoid are never on in the same step.
6. Every move that can collide has an interlock. The PLC cannot stop a coils-off motion, and an
   emergency stop or power loss switches all coils off in any step. Check each actuator's coils-off
   motion against where the other actuators can be in every step, and interlock the other actuator
   so it is never in that path.
7. Stop ends the cycle at a safe point. A move's coil stays on until its end sensor. What an
   actuator does when its coils go off (alarm, emergency stop) is in Pneumatics: a double-solenoid
   5/2 drives on to the end, a spring-return valve returns, a 5/3 closed centre stops in place.
8. The PLC program is not a safety function. The emergency stop's description in the I/O list says
   what it cuts in hardware (outputs, air); while that is unknown, it is an open question. An
   emergency stop that only the PLC reads is a stop function, not an emergency stop. Either way, it
   ends in `S90` and requires homing.
9. A broken wire reads 0. For buttons, switches and permissives, 0 is the safe meaning (stop, not
   ready, single cycle); where the wiring gives the opposite, that is an open question.

## Open questions

```markdown
- [ ] **?3** Which cylinder does 1Y1A drive? Notes: "retract cylinder". Assumed: magazine cylinder.
```

Question, then the source wording quoted, then any assumption the spec relies on. Name every
affected tag.
