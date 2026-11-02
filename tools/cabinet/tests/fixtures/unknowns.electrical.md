# Test station with unknowns only: electrical

Status: test fixture

Test fixture for `tools/cabinet`: fictional devices and parts, not a real machine. Nothing
overflows on known values; row 2 overflows only with the placeholder widths of its unknown parts,
so `check` warns and exits 0.

## 2. Devices

| Designation | Label | Tag | Name | Part |
|---|---|---|---|---|
| `+CAB1-TC1` | ? | | 24 V DC power supply | [Testco TC-PSU-24](parts/testco-tc-psu-24.md) |
| `+CAB1-KE1` | ? | | PLC | ? |
| `+CAB1-KE2` | ? | | PLC extension | ? (?1) |
| `=MAG+CAB1-KF1` | ? | | Relay module 1 | [Testco TC-RELAY-110](parts/testco-tc-relay-110.md) |
| `=MAG+CAB1-KF2` | ? | | Relay module 2 | [Testco TC-RELAY-110](parts/testco-tc-relay-110.md) |

## 7. Layout

### Enclosures

| Location | Part | Notes |
|---|---|---|
| `+CAB1` | [Testco TC-BOX-300](parts/testco-tc-box-300.md) | |

### Rows

| Location | Row | Kind | Height | Contents |
|---|---|---|---|---|
| `+CAB1` | 1 | duct | ? | |
| `+CAB1` | 2 | rail | | `=MAG+CAB1-KF1`, `=MAG+CAB1-KF2`, `+CAB1-KE1`, `+CAB1-KE2` |
| `+CAB1` | 3 | duct | 60 | |
| `+CAB1` | 4 | rail | | `+CAB1-TC1` |

## 8. Open questions

- [ ] **?1** Which PLC extension is `+CAB1-KE2`? Devices, Part `?`. Test fixture.
