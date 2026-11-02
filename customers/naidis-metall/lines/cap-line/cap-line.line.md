# Cap line

Status: draft

Per the [line guide](../../../../docs/line-guide.md).

## 1. Stations

| # | Machine | Spec | Role |
|---|---|---|---|
| 1 | `magazine-swivel` | [spec](../../magazine-swivel/magazine-swivel.spec.md) | Takes caps from a stack and hands them on one at a time |
| 2 | `color-sorter` | [spec](../../color-sorter/color-sorter.spec.md) | Sorts caps by colour; the customer's existing station |

## 2. Transfers

| From | To | Transfer point | Ready signal |
|---|---|---|---|
| `magazine-swivel` | `color-sorter` | The swivel's dropdown position is the sorter's infeed | Sorter ready |

## 3. Signals

| Signal | Sender | Receiver | Medium | 1 = |
|---|---|---|---|---|
| Sorter ready | `color-sorter` ?, `LNK_SendReady` | `magazine-swivel` 4S1, `LNK_NextReady` | IR beam between the stations | The sorter can take a part |

## 4. Emergency stop zones

| Zone | Emergency stops | Stops |
|---|---|---|
| ? | `magazine-swivel` 0S5, `color-sorter` ? | ? (?1) |

## 5. HMI

On-site operator HMI for the line. Device ?, location ?, connection to the PLCs ? (?2).

| Screen | Shows | Operator can |
|---|---|---|
| Overview | Each station's step (`StepNo`), auto or manual (`PNL_Manual`), its lamps; the sorter ready signal | Nothing; Start, Stop and Reset stay on each station's panel |
| Alarms | Each station's active alarm with its text | ? (?3) |
| Counters | Caps handed on, caps per colour | ? |

| Machine | Alarm | Text |
|---|---|---|
| `magazine-swivel` | `S99_Alarm` from `S4_VacuumOn` | Cap not gripped: check the pickup and vacuum, then Reset |
| `magazine-swivel` | `S99_Alarm` from `S5_WaitNextReady` or `S6_SwvToDropdown`, part lost | Cap dropped: remove it, then Reset |
| `magazine-swivel` | `S99_Alarm`, any other step timeout | ? (?4) |
| `magazine-swivel` | `S9_MagEmpty` | Magazine empty: refill, then Start |
| `color-sorter` | ? | ? |

## 6. Open questions

- [ ] **?1** Does one emergency stop stop the whole line, or does each station have its own zone?
  Emergency stop zones. No source.
- [ ] **?2** Which HMI device, where is it mounted, and how does it reach the PLCs (protocol, IP
  addresses)? HMI. No source.
- [ ] **?3** May the operator acknowledge alarms on the HMI, or only on the panels? HMI, Alarms.
  Assumed: only on the panels, by Reset.
- [ ] **?4** The HMI needs the step an alarm came from, but the station program shows only
  `StepNo` = 99 in `S99_Alarm`. Should the machine spec add an internal `AlarmStep`, the step
  that went to `S99_Alarm`? HMI, Alarms.
