# Magazine and swivel station: electrical

Status: draft

Machine spec: [magazine-swivel.spec.md](magazine-swivel.spec.md). Designations per the
[electrical guide](../../../docs/electrical-guide.md).

## 1. Locations

| Location | Name | Notes |
|---|---|---|
| `+CAB1` | Control cabinet: PLC, supply, protection | ?1 |
| `+OP1` | Operator panel: buttons, key switch, lamps; holds PNL2 | |
| `+ST1` | Station plate: magazine, swivel, gripper, valve island, XMA2 | |

## 2. Devices

| Designation | Label | Tag | Name | Part |
|---|---|---|---|---|
| `+CAB1-KE1` | ? | | PLC | ? (spec ?1) |
| `+CAB1-TC1` | ? | | 24 V DC power supply | ? |
| `+CAB1-FC1` | ? | | Supply protection | ? |
| `+CAB1-XD1` | ? | | Terminal strip: 24 V and 0 V distribution | ? |
| `+OP1-XG1` | PNL2 | | Control panel I/O: 8 I, 8 O | ? |
| `+ST1-XG2` | XMA2 | | I/O terminal block: 8 I, 8 O | ? |
| `+ST1-QM1` | 0V1 | | Valve island | ? |
| `=PNL+OP1-SJ1` | ? | 0S1 | Start button | ? |
| `=PNL+OP1-SJ2` | ? | 0S2 | Stop button, NC | ? |
| `=PNL+OP1-SJ3` | ? | 0S3 | Key switch auto / manual | ? |
| `=PNL+OP1-SJ4` | ? | 0S4 | Reset button | ? |
| `=PNL-SJ5` | ? | 0S5 | Emergency stop; location ? (spec ?2) | ? |
| `=PNL+OP1-PF1` | ? | 0H1 | Start button lamp | ? |
| `=PNL+OP1-PF2` | ? | 0H2 | Reset button lamp | ? |
| `=PNL+OP1-PF3` | `Q1` | 0H3 | Indicator lamp `Q1` | ? |
| `=PNL+OP1-PF4` | `Q2` | 0H4 | Indicator lamp `Q2` | ? |
| `=MAG+ST1-BG1` | ? | 1S1 | Magazine cylinder extended | ? |
| `=MAG+ST1-BG2` | ? | 1S2 | Magazine cylinder retracted | ? |
| `=MAG+ST1-BG3` | ? | 1S3 | Part at pickup | ? |
| `=MAG+ST1-MB1` | ? | 1Y1A | Magazine cylinder valve coil | ? |
| `=GRP+ST1-BP1` | ? | 2S1 | Gripper vacuum switch | ? |
| `=GRP+ST1-MB1` | ? | 2Y1A | Gripper valve coil: vacuum on | ? |
| `=GRP+ST1-MB2` | ? | 2Y1B | Gripper valve coil: vacuum off | ? |
| `=SWV+ST1-BG1` | ? | 3S1 | Swivel at pickup | ? |
| `=SWV+ST1-BG2` | ? | 3S2 | Swivel at dropdown | ? |
| `=SWV+ST1-MB1` | ? | 3Y1A | Swivel valve coil: to pickup | ? |
| `=SWV+ST1-MB2` | ? | 3Y1B | Swivel valve coil: to dropdown | ? |
| `=LNK+ST1-BG1` | ? | 4S1 | IR receiver from the colour sorter | ? |

## 3. Supply and protection

| Designation | Feeds | Rating |
|---|---|---|
| ? | Incoming supply to `+CAB1` | ? (?2) |
| `+CAB1-FC1` | `+CAB1-TC1` | ? |
| `+CAB1-TC1` | 24 V DC: `+CAB1-KE1`, `+OP1-XG1`, `+ST1-XG2`, `+ST1-QM1` | ? |

## 4. Safety circuit

| Safety function | Devices | Cuts | Stop category |
|---|---|---|---|
| Emergency stop | `=PNL-SJ5`, ? | ? (spec ?2) | ? |

## 5. Cables

| Cable | Type | From | To | Cores |
|---|---|---|---|---|
| `+CAB1-WG1` | ? | `+CAB1-KE1`, PLC connection 1 | `+OP1-XG1` | ? |
| `+CAB1-WG2` | ? | `+CAB1-KE1`, PLC connection 2 | `+ST1-XG2` | ? |
| ? | ? | Each sensor and coil | `+ST1-XG2` or `+ST1-QM1` | ? (?4) |

## 6. Connections

One row per signal conductor so far; supply and 0 V conductors are added with section 3.

| From | To | Via | Size | Colour |
|---|---|---|---|---|
| `=PNL+OP1-SJ1:?` | `+OP1-XG1:O0` | ? | ? | ? |
| `=PNL+OP1-SJ2:?` | `+OP1-XG1:O1` | ? | ? | ? |
| `=PNL+OP1-SJ3:?` | `+OP1-XG1:O2` | ? | ? | ? |
| `=PNL+OP1-SJ4:?` | `+OP1-XG1:O3` | ? | ? | ? |
| `=PNL-SJ5:?` | ? | ? | ? | ? |
| `+OP1-XG1:I0` | `=PNL+OP1-PF1:?` | ? | ? | ? |
| `+OP1-XG1:I1` | `=PNL+OP1-PF2:?` | ? | ? | ? |
| `+OP1-XG1:I2` | `=PNL+OP1-PF3:?` | ? | ? | ? |
| `+OP1-XG1:I3` | `=PNL+OP1-PF4:?` | ? | ? | ? |
| `=MAG+ST1-BG1:?` | `+ST1-XG2:I1` | ? | ? | ? |
| `=MAG+ST1-BG2:?` | `+ST1-XG2:I2` | ? | ? | ? |
| `=GRP+ST1-BP1:?` | `+ST1-XG2:I3` | ? | ? | ? |
| `=SWV+ST1-BG1:?` | `+ST1-XG2:I4` | ? | ? | ? |
| `=SWV+ST1-BG2:?` | `+ST1-XG2:I5` | ? | ? | ? |
| `=MAG+ST1-BG3:?` | `+ST1-XG2:I6` | ? | ? | ? |
| `=LNK+ST1-BG1:?` | ? | ? | ? | ? |
| `+ST1-XG2:O0` | `=MAG+ST1-MB1:?` | ? | ? | ? |
| `+ST1-XG2:O1` | `=GRP+ST1-MB1:?` | ? | ? | ? |
| `+ST1-XG2:O2` | `=GRP+ST1-MB2:?` | ? | ? | ? |
| `+ST1-XG2:O3` | `=SWV+ST1-MB1:?` | ? | ? | ? |
| `+ST1-XG2:O4` | `=SWV+ST1-MB2:?` | ? | ? | ? |

## 7. Layout

Enclosure and row order are not known yet (?6, ?7).

### Enclosures

| Location | Part | Notes |
|---|---|---|
| `+CAB1` | ? | ?6 |

### Rows

| Location | Row | Kind | Height | Contents |
|---|---|---|---|---|
| `+CAB1` | 1 | duct | ? | |
| `+CAB1` | 2 | rail | | `+CAB1-FC1`, `+CAB1-TC1`, `+CAB1-XD1` |
| `+CAB1` | 3 | duct | ? | |
| `+CAB1` | 4 | rail | | `+CAB1-KE1` |
| `+CAB1` | 5 | duct | ? | |

## 8. Open questions

- [ ] **?1** Is there a control cabinet, or is the PLC mounted on the station plate? Locations,
  `+CAB1`. No source. Assumed: a cabinet `+CAB1`.
- [ ] **?2** What feeds the station: mains to the cabinet, or 24 V DC from the customer? Supply,
  rating `?`. No source.
- [ ] **?3** What does the emergency stop cut in hardware, through which devices, and at which stop
  category? Safety circuit; the same unknown as spec ?2.
- [ ] **?4** Which connector and pin does each sensor and coil use, and through which cable?
  Connections, terminals `:?`. No source.
- [ ] **?5** Are `BG`, `BP`, `MB` and `QM`, and `SJ` for the emergency stop, the right
  IEC 81346-2:2019 codes? Devices; marked "verify" in the guide's letter codes.
- [ ] **?6** Which enclosure is `+CAB1`, and what size is its mounting plate? Layout, enclosure
  Part `?`. No source.
- [ ] **?7** Is the row order right? Layout, rows. No source. Assumed: supply and protection on the
  upper rail, PLC on the rail below it, a duct above, between and below. To be confirmed with the
  cabinet builder.
