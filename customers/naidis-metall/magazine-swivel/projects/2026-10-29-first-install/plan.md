# Magazine and swivel station: project plan

Status: planning

Demo scenario: the customer, its parts, people and dates are fictional. The station is the one in
the [spec](../../spec.md); the program is [`plc/`](../../plc/).

## 1. Brief

Näidis Metall OÜ turns aluminium end caps for LED light profiles. The caps come back from the
anodiser in crates and go to the customer's laser marker, which engraves the logo on the flat
face. Today an operator takes caps from the crate and lays them on the marker's infeed belt one at
a time, all shift. The customer wants a station that takes a stack of caps and puts them on the
belt one by one, so the operator only loads the magazine and handles faults.

| Customer asked for | Answered by |
|---|---|
| "Load a stack and walk away." | Magazine 1A1 pushes the bottom cap to pickup; auto (`PNL_Manual` = 0) repeats the cycle S1–S7 |
| "Don't touch the anodised face." | Vacuum gripper 2A1 on the swivel 3A1; no jaws |
| "Tell us when it runs out, don't just stop." | `MAG_PickupOccupied` after the push; `S8_MagEmpty` waits for a refill and Start |
| "No cap may end up on the floor unnoticed." | `GRP_PartGripped` before the turn (S4) and during it (S5); else `S99_Alarm` |
| "Our setter needs one cap at a time while setting up the marker." | Key switch to manual: one cycle per Start |
| "Stop means finish the cap, not drop it." | Stop sets StopReq; the cycle ends in S7, then S0 |
| "After an emergency stop or a fault it must not move until someone says so." | `S90_HomingRequired` and `S99_Alarm` are left only by Reset↑, into homing |
| "Use the panel and valve island we already have." | Components PNL2, XMA2, 0V1 |

## 2. Team

| Role | Who | Responsible for |
|---|---|---|
| Project lead | Integrator | This plan, the customer contact, the commissioning day |
| Controls engineer | Integrator | Spec, PLC program, sim tests, downloading the `hw` target on site |
| Production manager | Näidis Metall | Approving the spec, the commissioning window, the operators' time |
| Setter | Näidis Metall | Sample caps, the marker's trial job, accepting the station at the marker |
| Electrician | Näidis Metall | Panel and emergency stop wiring, power and air at the station |

## 3. Goal

The marker is fed from the magazine instead of by hand, and no cap reaches the belt or the floor
without the station knowing. The operator's job becomes loading the magazine and clearing faults.

What a shift looks like afterwards: the operator fills the magazine from the crate. If the station
was stopped normally the evening before, it powers up at Home and is ready. With the key switch on
auto, one Start runs it until the stack runs out; then it waits in `S8_MagEmpty` until the operator
refills and presses Start. At the end of the shift Stop lets the current cap reach the belt and
the station stops at Home.

If a cap is not gripped or slips off during the turn, the station stops in `S99_Alarm`. The
operator removes the cap and presses Reset; the station homes and is ready again. After an
emergency stop all coils go off: the magazine cylinder springs forward, the swivel stops where it
is and the gripper may let go of its cap. The operator clears the station, releases the emergency
stop and presses Reset to home it. The pusher and the swivel share the pickup position, which is
why each may move there only while the other is clear (spec, interlocks).

## 4. Result

In priority order:

1. The emergency stop 0S5 is wired, and what it cuts in hardware is known and tested.
2. Every interlock and every safety rule of the spec guide is checked on the machine and recorded.
3. A full magazine runs in auto onto the marker belt with no cap lost or misplaced.
4. Magazine empty, part not gripped, part lost and emergency stop behave on the machine as in the
   sim tests.
5. The spec has no `?` left and its status line reads `commissioned`.
6. Operators and the setter are trained and have the operating card at the station.

## 5. Constraints

- The marker runs two shifts on weekdays; the station is installed and commissioned on a Saturday,
  with Sunday in reserve. By Monday morning the marker must run, with or without the station.
- The panel PNL2, terminal block XMA2 and valve island 0V1 are the customer's and stay.
- The marker's belt has its own part sensor and buffers caps, so the station has no handshake with
  the marker: it drops a cap whenever it has one. A "marker ready" signal is a later change.
- Three items are `?` in the spec until the site visit: the PLC model, the emergency stop's address
  and what it cuts, and the gripper valve 2V1 type.

## 6. Activities

### 6.1 Preparation

Everything that can be settled before the station leaves the workshop.

| Activity | Owner | NLT |
|---|---|---|
| Review the spec with the customer; record it in the status line | Controls engineer, production manager | 2026-11-06 |
| Site visit: read the PLC model and the 2V1 label, trace where 0S5 is wired and what it cuts; apply the answers to the spec, the commit naming the evidence | Controls engineer, electrician | 2026-11-06 |
| Send sample caps of every variant the marker runs | Setter | 2026-11-06 |
| Agree the commissioning Saturday and that the marker is free that day | Project lead, production manager | 2026-11-06 |
| Set up a separate marker job for the trials, so test caps never run on a production job | Setter | 2026-11-13 |
| Order spares: suction cup for 2A1, one of each sensor type in the I/O list | Project lead | 2026-11-06 |

Prerequisites: the spec draft is complete apart from its `?` items.

End result: the spec is reviewed and has no `?`; the date, the sample caps and the trial job are
settled; spares are ordered.

### 6.2 Simulation and workshop test

| Activity | Owner | NLT |
|---|---|---|
| Update `src/`, `tests/` and `targets/hw.st` to the reviewed spec; all sim tests pass (`tools/openplc/openplc.py test magazine-swivel`) | Controls engineer | 2026-11-13 |
| Compile the `hw` target for the PLC model from the site visit (`check -t hw`) | Controls engineer | 2026-11-13 |
| Workshop test on the station mechanics with the sample caps: every variant feeds from the magazine and grips on vacuum; the sim scenarios repeated by hand | Project lead, controls engineer | 2026-11-18 |
| Write the operating card: what Start, Stop, Reset and the key switch do, and what each lamp state means | Controls engineer | 2026-11-18 |

Prerequisites: preparation is done; sample caps received.

End result: the program passes in sim and compiles for the real PLC; every cap variant has run on
the real mechanics, or is named as out of scope with the production manager's agreement.

### 6.3 Commissioning

Saturday 2026-11-21, reserve Sunday 2026-11-22. In this order; the riskiest checks come first, so a
setback leaves the reserve day for it.

| Activity | Owner | NLT |
|---|---|---|
| Photograph the marker infeed before work starts, so it can be put back as it was | Project lead | 2026-11-21 |
| Mount the station, connect air and power | Project lead, electrician | 2026-11-21 |
| Check the emergency stop: what it cuts, measured with the station powered and air on | Electrician, controls engineer | 2026-11-21 |
| I/O check with air off, row by row against the I/O list: each input operated by hand, each lamp and coil seen | Controls engineer, electrician | 2026-11-21 |
| Download the `hw` target (by the controls engineer, never by an agent) | Controls engineer | 2026-11-21 |
| Check each interlock and each safety rule of the spec guide; record the result per rule | Controls engineer | 2026-11-21 |
| Repeat the sim scenarios on the machine: one cycle, held Start, auto until empty, Stop, part lost, part not gripped, swivel jam, emergency stop | Controls engineer | 2026-11-21 |
| Set the timeouts and the vacuum-off time on test with real caps; changed values go into the spec, the commit naming the test | Controls engineer | 2026-11-22 |
| Run a full magazine in auto on the trial job | Setter, controls engineer | 2026-11-22 |
| Switch the marker back to its production job; the setter checks it | Setter | 2026-11-22 |

Prerequisites: simulation and workshop test are done. The electrician and setter are confirmed two
days before. Spares, tools and the operating card are at the station the evening before.

End result: result lines 1–4 are true; the marker is on its production job.

### 6.4 Handover

| Activity | Owner | NLT |
|---|---|---|
| Train each shift's operators and the setter at the station, with the operating card | Project lead | 2026-11-23 |
| Stay at the station through the first shift | Project lead | 2026-11-23 |
| Log every `S99_Alarm` in the first week with its cause; adjust a timeout only on that evidence | Setter, controls engineer | 2026-11-30 |
| Set the spec status to `commissioned` | Controls engineer | 2026-11-30 |
| Write the retrospective (section 8) | Project lead | 2026-12-04 |

End result: result lines 5 and 6 are true; the plan is closed.

## 7. Risks

### Emergency stop cuts nothing in hardware

The site visit may find 0S5 wired only to a PLC input, or not at all. Then it is a stop function,
not an emergency stop.

- Likelihood: medium. Impact: high; the station cannot be handed over.
- Mitigable: fully.
- Countermeasures: trace 0S5 at the site visit, not on the day. If it is PLC-only, the production
  manager decides on a hardware safety circuit before the date is confirmed.

### Gripper valve differs from the spec

2V1 is `?`. A valve that holds vacuum with its coils off changes what the gripper does on an
emergency stop.

- Likelihood: medium. Impact: medium; Pneumatics and the coils-off check of safety rule 6 change.
- Mitigable: fully.
- Countermeasures: read the label at the site visit; redo the rule 6 check in the spec before the
  workshop test.

### A cap variant does not feed or grip

Variants differ in size and finish; one may jam in the magazine or not reach vacuum.

- Likelihood: medium. Impact: high; that variant stays on manual loading.
- Mitigable: partly.
- Countermeasures: try every variant at the workshop test. A failing variant is out of scope for
  this project, agreed with the production manager before commissioning, not found on site.

### Commissioning overruns the weekend

- Likelihood: low. Impact: high; the marker loses production on Monday.
- Mitigable: partly.
- Countermeasures: riskiest checks first on Saturday; Sunday is reserve. If the station is not
  accepted by Sunday evening, it is switched off, the infeed is restored from the photographs and
  the operator loads by hand on Monday.

### Trials disturb the marker's production job

- Likelihood: low. Impact: high; wrong logos on customer parts.
- Mitigable: fully.
- Countermeasures: trials run only on the separate marker job; the setter switches back and checks.

### Nuisance alarms in the first weeks

Timeouts set on a few test cycles may be too tight for a full shift.

- Likelihood: medium. Impact: medium; operators lose trust and load by hand.
- Mitigable: fully.
- Countermeasures: the project lead on the first shift; the first-week alarm log; a timeout changes
  only on a logged cause.

### Customer staff not there on the day

- Likelihood: low. Impact: high; no emergency stop check, no trial job.
- Mitigable: partly.
- Countermeasures: confirm the electrician and setter two days before; the production manager names
  a stand-in for each.

## 8. Retrospective

Written after handover, by the project lead. The questions are in the
[plan guide](../../../../../docs/plan-guide.md#retrospective).
