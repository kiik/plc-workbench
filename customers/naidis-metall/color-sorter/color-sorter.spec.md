# Colour sorter

Status: draft

The customer's existing station after the magazine and swivel station on the
[cap line](../lines/cap-line/cap-line.line.md). This spec is taken from its labels and program at
the site visit; until then only its end of the line link is known.

## 1. Modules

| Module | Name | Local name | Groups |
|---|---|---|---|
| SRT | Sorter | | ? |
| LNK | Line link to the magazine and swivel station | | ? |

## 2. Components

| Tag | Name | Local name | Notes |
|---|---|---|---|
| ? | PLC | | Model ? |

## 3. Pneumatics

| Actuator | Name | Valve | Valve type | Coils | Coils off |
|---|---|---|---|---|---|
| ? | ? | ? | ? | ? | ? |

## 4. I/O list

| Tag | Address | Direction | Symbol | Description |
|---|---|---|---|---|
| ? | ? | output | `LNK_SendReady` | IR transmitter to the magazine and swivel station: 1 = can take a part |

## 5. Control

? (?2)

## 6. Open questions

- [ ] **?1** Which PLC, I/O devices, actuators and labels does the sorter have? All sections. To be
  read at the site visit.
- [ ] **?2** Is the sorter's existing program kept, or is it written new to this repo's guides?
  Control. No source.
- [ ] **?3** Which tag and terminal drive the IR transmitter, and in which steps is it on? I/O list.
  Request: "the sorter returns availability signal, when it can take in new parts".
- [ ] **?4** How does the sorter detect colour, and into how many bins does it sort? Components,
  Control. No source.
